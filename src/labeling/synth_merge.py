import numpy as np
import pandas as pd
import yaml
from pathlib import Path

OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

def clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)

def deep_merge(a: dict, b: dict) -> dict:
    out = dict(a or {})
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_cfg(path="config/life_profile.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def synth_one_profile(n: int, seed: int, env_df: pd.DataFrame, params: dict, profile_name: str) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # directions: phone-, caffeine-, activity+, env-
    dir_phone, dir_caf, dir_act, dir_env = -1, -1, +1, -1

    # weights
    k_phone = float(params.get("k_phone", 0.25))
    k_caf   = float(params.get("k_caf", 0.18))
    k_act_p = float(params.get("k_act_p", 0.12))
    k_act_n = float(params.get("k_act_n", 0.02))
    k_env   = float(params.get("k_env", 0.30))
    k_debt  = float(params.get("k_debt", 0.25))

    # mood weights
    mood_sleep_gain = float(params.get("mood_sleep_gain_per_h", 6.0))
    mood_act_gain   = float(params.get("mood_activity_gain_per_h", 1.5))
    mood_caf_pen    = float(params.get("mood_caffeine_penalty_per_cup", -1.0))
    mood_env_pen    = float(params.get("mood_env_penalty_per_unit", -5.0))
    mood_phone_pen  = float(params.get("mood_phone_penalty_per_h", -0.6))

    # env weights
    ew = params.get("env_weights", {}) or {}
    pm_w   = float(ew.get("pm_weight", 0.33))
    temp_w = float(ew.get("temp_weight", 0.34))
    hum_w  = float(ew.get("hum_weight", 0.33))
    t0     = float(ew.get("temp_comfort_c", 21))
    h0     = float(ew.get("hum_comfort_pct", 45))

    # bases/noise/bounds/rules
    bases  = params.get("bases", {}) or {}
    noise  = params.get("noise", {}) or {}
    bounds = params.get("bounds", {}) or {}
    rules  = params.get("rules", {}) or {}

    sleep_base = float(bases.get("sleep_base_h", 7.2))
    phone_base = float(bases.get("phone_base_h", 3.8))
    act_base   = float(bases.get("activity_base_h", 5.0))
    caf_min    = int(bases.get("caffeine_base_cups_min", 0))
    caf_max    = int(bases.get("caffeine_base_cups_max", 4))

    sleep_noise = float(noise.get("sleep_noise_h", 0.6))
    mood_noise  = float(noise.get("mood_noise_pts", 6.0))
    phone_noise = float(noise.get("phone_noise_h", 1.0))
    act_noise   = float(noise.get("activity_noise_h", 1.6))

    sleep_min = float(bounds.get("sleep_min_h", 4))
    sleep_max = float(bounds.get("sleep_max_h", 10))
    phone_min = float(bounds.get("phone_min_h", 0))
    phone_max = float(bounds.get("phone_max_h", 12))
    act_min   = float(bounds.get("activity_min_h", 0))
    act_max   = float(bounds.get("activity_max_h", 12))
    caf_abs_min = int(bounds.get("caffeine_min_cups", 0))
    caf_abs_max = int(bounds.get("caffeine_max_cups", 6))

    phone_stress_gain = float(rules.get("phone_stress_gain_h", 0.4))
    act_stress_drop   = float(rules.get("activity_stress_drop_h", 0.5))
    over_act_th       = float(rules.get("over_activity_threshold_h", 7.0))
    debt_gate_h       = float(rules.get("caffeine_reduce_if_debt_gt_h", 1.5))
    debt_reduce_rng   = rules.get("caffeine_reduce_range_cups", [0, 1])

    # --- env_merged.csv 사용: 길이 n에 맞게 반복/자르기 ---
    pm_arr   = np.resize(env_df["PM10"].to_numpy(), n)
    temp_arr = np.resize(env_df["Temp"].to_numpy(), n)
    hum_arr  = np.resize(env_df["Humidity"].to_numpy(), n)

    pm_std  = (pm_arr - np.nanmean(pm_arr)) / (np.nanstd(pm_arr) + 1e-9)
    temp_dev = np.abs(temp_arr - t0) / 8.0
    hum_dev  = np.abs(hum_arr - h0) / 20.0

    env_stress = pm_w * (1.0 / (1 + np.exp(-pm_std))) + temp_w * temp_dev + hum_w * hum_dev
    if dir_env > 0:
        env_stress = -env_stress

    # buffers
    n = int(n)
    sleep = np.zeros(n)
    caf   = np.zeros(n, dtype=int)
    phone = np.zeros(n)
    act   = np.zeros(n)
    mood  = np.zeros(n)
    debt  = np.zeros(n)

    sleep[0] = clamp(rng.normal(sleep_base, sleep_noise), sleep_min, sleep_max)
    caf[0]   = int(clamp(rng.integers(caf_min, caf_max + 1), caf_abs_min, caf_abs_max))
    phone[0] = clamp(rng.normal(phone_base, phone_noise), phone_min, phone_max)
    act[0]   = clamp(rng.normal(act_base, act_noise), act_min, act_max)
    debt[0]  = max(0.0, 7 - sleep[0])

    for t in range(n):
        if t > 0:
            reduce = rng.integers(debt_reduce_rng[0], debt_reduce_rng[1] + 1) if debt[t-1] > debt_gate_h else 0
            caf[t] = int(clamp(rng.integers(caf_min, caf_max + 1) - reduce, caf_abs_min, caf_abs_max))
            phone[t] = clamp(rng.normal(phone_base + phone_stress_gain * env_stress[t], phone_noise), phone_min, phone_max)
            act[t]   = clamp(rng.normal(act_base - act_stress_drop * env_stress[t], act_noise), act_min, act_max)

            over_pen = max(0.0, act[t] - over_act_th)
            sleep_mean = (
                7.0
                + k_phone * (-dir_phone) * phone[t]
                + k_caf   * (-dir_caf)   * caf[t]
                + k_act_p * (+dir_act)   * act[t]
                - k_act_n * (+dir_act)   * over_pen
                + k_env   * (-dir_env)   * env_stress[t]
                + k_debt * debt[t-1]
            )
            sleep[t] = clamp(rng.normal(sleep_mean, sleep_noise), sleep_min, sleep_max)

            recent = np.mean(sleep[max(0, t-2):t+1])
            debt[t] = max(0.0, 7 - recent)

        mood_mean = (
            60
            + mood_sleep_gain * (sleep[t] - 7)
            + mood_act_gain   * act[t]
            + mood_caf_pen    * caf[t]
            + mood_env_pen    * env_stress[t]
            + mood_phone_pen  * phone[t]
        )
        mood[t] = clamp(rng.normal(mood_mean, mood_noise), 0, 100)

    return pd.DataFrame({
        "SleepTime": sleep,
        "MoodScore": mood,
        "ActivityTime": act,
        "Caffeine": caf,
        "PhoneTime": phone,
        "PM10": pm_arr,
        "Temp": temp_arr,
        "Humidity": hum_arr,
        "profile_type": profile_name
    })

def main():
    cfg = load_cfg("config/life_profile.yaml")
    defaults = cfg.get("defaults", {})
    profiles = cfg.get("profiles", [])
    seed = cfg.get("seed", 42)

    # env_merged.csv 미리 로드(한 번만)
    env_df = pd.read_csv(OUT / "env_merged.csv")

    rng = np.random.default_rng(seed)
    all_dfs = []

    for prof in profiles:
        name = prof["name"]
        rows = int(prof.get("rows", 1000))
        params = deep_merge(defaults, prof.get("overrides", {}))

        # 인자 이름을 params로 통일
        df_p = synth_one_profile(
            n=rows,
            seed=int(rng.integers(0, 1_000_000_000)),
            env_df=env_df,
            params=params,
            profile_name=name
        )
        fp = OUT / f"synth_{name}.csv"
        df_p.to_csv(fp, index=False, encoding="utf-8")
        print(f"[INFO] saved {fp} shape={df_p.shape}")
        all_dfs.append(df_p)

    all_df = pd.concat(all_dfs, ignore_index=True)
    all_df.to_csv(OUT / "life_synth_merged.csv", index=False, encoding="utf-8")
    print(f"[INFO] saved life_synth_merged.csv shape={all_df.shape}")

if __name__ == "__main__":
    main()
