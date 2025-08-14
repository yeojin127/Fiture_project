import numpy as np
import pandas as pd
import yaml
from pathlib import Path

#결과 저장 주소
OUT = Path("data/processed")

#값이 너무 작으면 lo, 너무 크면 hi로
def _clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)

#yaml 파일에서 설정 불러오기 (방향(변수 증가할 때 잠이 증가 or 감소 방향), 계수(영향 크기))
def load_profile(path="config/life_profile.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
# n : 일수, seed : 난수고정, env_df : 환경 데이터, profile : yaml정보, rng : 난수 생성기
def synthesize_life_data(n: int, seed: int, env_df: pd.DataFrame | None, profile: dict) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # 방향(+1/-1) 설정
    dir_phone = int(profile["directions"].get("phone", -1))
    dir_caf   = int(profile["directions"].get("caffeine", -1))
    dir_act   = int(profile["directions"].get("activity", +1))
    dir_env   = int(profile["directions"].get("environment", -1)) # 환경 스트레스가 잠에 미치는 방향성

    # 계수(세기) 읽기
    k = profile.get("coeff", {})
    k_phone = float(k.get("phone", 0.25)) # 폰 1시간 늘면 잠이 15분(0.25시간) 줄어든다
    k_caf   = float(k.get("caffeine", 0.18))
    k_act_p = float(k.get("activity_pos", 0.12))
    k_act_n = float(k.get("activity_neg", 0.02))
    k_env   = float(k.get("environment", 0.30))
    k_debt  = float(k.get("sleep_debt", 0.25))

    # 환경 스트레스 지표 설정
    # numpy 배열로 불러오기
    pm = env_df["PM10"].to_numpy()
    temp = env_df["Temp"].to_numpy() 
    hum = env_df["Humidity"].to_numpy() 

    # pm :표준화, hum : 45%에서 얼마나 벗어났는지, temp : 온도가 21도에서 얼마나 벗어났는지
    pm_std = (pm - np.nanmean(pm)) / (np.nanstd(pm) + 1e-6)
    hum_dev = np.abs(hum - 45) / 20.0
    temp_dev = np.abs(temp - 21) / 8.0

    # 세가지 변수 가중합 -> 환경 스트레스 (환경이 나쁠수록 커지는 점수)
    env_stress_raw = 0.6*(1/(1+np.exp(-pm_std))) + 0.2*hum_dev + 0.2*temp_dev
    # 환경 나쁨 정도
    env_stress = env_stress_raw if dir_env < 0 else -env_stress_raw  # 방향 전환

    #데이터 빈 상자들
    sleep = np.zeros(n)
    caf = np.zeros(n)
    phone = np.zeros(n)
    act = np.zeros(n)
    mood = np.zeros(n)
    debt = np.zeros(n)

    # 초기값 설정 (평균치에서 랜덤), 부채 첫날은 7시간 기준으로 부족한만큼 설정
    sleep[0] = _clamp(rng.normal(7.2, 0.6), 4, 10)
    caf[0] = rng.integers(0, 4)
    phone[0] = _clamp(rng.normal(4.0, 1.0), 0, 12)
    act[0] = _clamp(rng.normal(5.0, 1.5), 0, 12)
    debt[0] = max(0.0, 7 - sleep[0])


    for t in range(n):
        if t > 0:
            # 생활 패턴 가정
            caf[t] = _clamp(rng.integers(0, 5) - (debt[t-1] > 1.5)*rng.integers(0, 2), 0, 6)
            phone[t] = _clamp(rng.normal(3.8 + 0.4*env_stress[t], 1.0), 0, 12)
            act[t] = _clamp(rng.normal(5.0 - 0.5*env_stress[t], 1.6), 0, 12)

            # 수면 평균: 방향에 따라 부호 반영
            # dir_phone: +1이면 phone↑ → 잠↑, -1이면 phone↑ → 잠↓
            # act는 적당함의 곡선효과(+)와 과도함의 패널티(-) 분리
            sleep_mean = (
                7.0
                + (dir_phone * -1) * k_phone * phone[t]    # 기본은 phone↑ → 잠↓
                + (dir_caf   * -1) * k_caf   * caf[t]      # 기본은 caf↑ → 잠↓
                + (dir_act   * +1) * k_act_p * act[t]      # 활동의 긍정 효과
                - (dir_act   * +1) * k_act_n * (act[t]**2)/12  # 과도한 활동 패널티
                + (dir_env   * -1) * k_env   * env_stress[t]   # 기본은 환경스트레스↑ → 잠↓
                + k_debt * debt[t-1]                         # 수면부채 반동
            )
            sleep[t] = _clamp(rng.normal(sleep_mean, 0.6), 4, 10)

            recent = np.mean(sleep[max(0, t-2):t+1])
            debt[t] = max(0.0, 7 - recent)

        # 기분 점수(간단모델): 수면/활동/환경/폰/카페인
        mood_mean = 60 + 6.0*(sleep[t]-7) + 1.5*act[t] - 1.0*caf[t] - 5.0*env_stress[t] - 0.6*phone[t]
        mood[t] = _clamp(rng.normal(mood_mean, 6.0), 0, 100)

    return pd.DataFrame({
        "SleepTime": sleep,
        "MoodScore": mood,
        "ActivityTime": act,
        "Caffeine": caf.astype(int),
        "PhoneTime": phone
    })

if __name__ == "__main__":
    # 단독 실행 테스트용
    env = pd.read_csv("data/processed/env_merged.csv") if (Path("data/processed")/"env_merged.csv").exists() else None
    prof = load_profile()
    df = synthesize_life_data(n=len(env) if env is not None else 500, seed=42, env_df=env, profile=prof)
    df.to_csv(OUT / "life_synth.csv", index=False)
    print(f"[INFO] life_synth.csv saved, shape={df.shape}")
