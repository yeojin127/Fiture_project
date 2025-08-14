#!/usr/bin/env python
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

IN_PATH = Path("data/processed/dataset_merged.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = [
    "PM10", "Temp", "Humidity",
    "SleepTime", "ActivityTime", "Caffeine", "PhoneTime", "MoodScore"
]
TARGET_COL = "ConditionLabel"
ID_COLS = ["date"]


def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def make_condition_score(row):
    """
    ① 점수 분포를 고르게 만들기 위한 조정 버전
    - 시작점 낮춤: 30
    - 나쁜 요인 감점 강화: PhoneTime, PM10, Caffeine
    - 좋은 요인 보너스는 보수적으로
    """
    score = 30.0  # 낮은 시작점

    # 좋은 요인 (+)
    sleep = row.get("SleepTime", 0.0)
    activity = row.get("ActivityTime", 0.0)
    temp = row.get("Temp", np.nan)
    hum = row.get("Humidity", np.nan)
    ms = row.get("MoodScore", 50.0)

    score += 16.0 * min(sleep / 7.5, 1.2)       # 7.5h 기준, 과보너스 제한
    score += 8.0 * min(activity / 1.5, 1.5)     # 1.5h 기준
    if pd.notna(temp) and 18 <= temp <= 24:
        score += 4.0                              # 쾌적 온도 보너스
    if pd.notna(hum) and 40 <= hum <= 60:
        score += 4.0                              # 쾌적 습도 보너스

    score += 0.25 * ms                           # 사용자 입력 MoodScore(최대 +25)

    # 나쁜 요인 (−)
    caf = row.get("Caffeine", 0.0)
    phone = row.get("PhoneTime", 0.0)
    pm10 = row.get("PM10", 0.0)

    score -= 12.0 * min(caf / 3.0, 1.5)          # 3잔 기준
    score -= 18.0 * min(phone / 5.0, 1.5)        # 5시간 기준
    score -= 20.0 * min(pm10 / 100.0, 2.0)       # 100 µg/m³ 기준

    return clamp(round(score))


def label_absolute(x):
    """
    ② 절대 컷(보수적 경계) - 이전보다 한 단계씩 엄격하게
    <50 → 1, <60 → 2, <70 → 3, <80 → 4, ≥80 → 5
    """
    if x < 50:
        return 1
    if x < 60:
        return 2
    if x < 70:
        return 3
    if x < 80:
        return 4
    return 5


def label_quantile(scores: pd.Series) -> pd.Series:
    """
    ③ 분위수 컷(20/40/60/80%) - 라벨 균형 목적
    """
    try:
        return pd.qcut(scores, q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    except ValueError:
        # 경계 값이 겹칠 때 완화
        return pd.qcut(scores, q=5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)


def needs_rebalance(labels: pd.Series, low_floor=0.10, high_ceiling=0.40) -> bool:
    """
    ④ 분포 쏠림 감지: 어떤 라벨이 10% 미만이거나 40% 초과면 재밸런싱 권고
    """
    counts = labels.value_counts(normalize=True)
    return (counts.lt(low_floor).any()) or (counts.gt(high_ceiling).any())


def main(args):
    # 1) 읽기
    df = pd.read_csv(IN_PATH)
    df.columns = [c.strip() for c in df.columns]

    # 2) 불필요 열 제거
    if "region" in df.columns:
        df = df.drop(columns=["region"])

    # 3) 기대 컬럼 점검
    expected_cols = ["date"] + FEATURE_COLS
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        print(f"[WARN] Missing columns in dataset: {missing}")

    # 4) 점수 생성
    df["ConditionScore"] = df.apply(make_condition_score, axis=1)

    # 5) 라벨링: 모드 선택
    mode = args.labeling.lower()
    if mode not in {"auto", "absolute", "quantile"}:
        raise ValueError("--labeling must be one of {auto, absolute, quantile}")

    if mode == "absolute":
        df[TARGET_COL] = df["ConditionScore"].apply(label_absolute).astype(int)
        used_mode = "absolute"
    elif mode == "quantile":
        df[TARGET_COL] = label_quantile(df["ConditionScore"])
        used_mode = "quantile"
    else:
        # auto: 절대컷 → 분포 확인 → 필요하면 분위수로 재라벨
        abs_labels = df["ConditionScore"].apply(label_absolute).astype(int)
        if needs_rebalance(abs_labels):
            print("[INFO] Class imbalance detected with absolute cut. Re-labeling with quantiles.")
            df[TARGET_COL] = label_quantile(df["ConditionScore"])
            used_mode = "auto->quantile"
        else:
            df[TARGET_COL] = abs_labels
            used_mode = "auto->absolute"

    # 6) 준비데이터 생성
    keep_cols = ID_COLS + FEATURE_COLS + ["ConditionScore", TARGET_COL]
    df_ready = df[keep_cols].copy()
    df_ready = df_ready.dropna(subset=FEATURE_COLS + ["ConditionScore", TARGET_COL])

    # 7) 저장(전체셋)
    ready_path = OUT_DIR / "dataset_ready.csv"
    df_ready.to_csv(ready_path, index=False)
    print(f"[INFO] saved {ready_path} shape={df_ready.shape}")

    # 라벨 분포 출력
    dist = df_ready[TARGET_COL].value_counts().sort_index()
    print("[INFO] label distribution:")
    print(dist)
    print("[INFO] label ratio:")
    print((dist / dist.sum()).round(3))

    # 8) 학습/검증 분할(라벨 분포 유지)
    train_df, valid_df = train_test_split(
        df_ready,
        test_size=0.2,
        random_state=20250814,
        stratify=df_ready[TARGET_COL]
    )
    train_path = OUT_DIR / "train.csv"
    valid_path = OUT_DIR / "valid.csv"
    train_df.to_csv(train_path, index=False)
    valid_df.to_csv(valid_path, index=False)
    print(f"[INFO] saved {train_path} shape={train_df.shape}")
    print(f"[INFO] saved {valid_path} shape={valid_df.shape}")

    # 9) feature_config.json 저장
    feature_config = {
        "id_cols": ID_COLS,
        "target": TARGET_COL,
        "features": [
            {"name": "PM10", "type": "numerical", "unit": "µg/m³", "desc": "미세먼지 농도 (낮을수록 좋음)"},
            {"name": "Temp", "type": "numerical", "unit": "°C", "desc": "평균 기온 (18~24℃ 쾌적)"},
            {"name": "Humidity", "type": "numerical", "unit": "%", "desc": "상대 습도 (40~60% 쾌적)"},
            {"name": "SleepTime", "type": "numerical", "unit": "hours", "desc": "수면 시간 (7~8시간 권장)"},
            {"name": "ActivityTime", "type": "numerical", "unit": "hours", "desc": "활동/운동 시간"},
            {"name": "Caffeine", "type": "numerical", "unit": "cups", "desc": "카페인 섭취량(잔) (적을수록 좋음)"},
            {"name": "PhoneTime", "type": "numerical", "unit": "hours", "desc": "휴대폰 사용 시간 (적을수록 좋음)"},
            {"name": "MoodScore", "type": "numerical", "unit": "points", "desc": "사용자 입력 기분 점수(0~100)"},
        ],
        "aux": {
            "score_name": "ConditionScore",
            "score_range": [0, 100],
            "labeling_mode": used_mode,
            "absolute_cut": "<50→1, 50-59→2, 60-69→3, 70-79→4, ≥80→5",
            "rebalance_rule": "if any class <10% or >40%, switch to quantile(20/40/60/80)",
            "split": {"test_size": 0.2, "random_state": 20250814, "stratify": True}
        }
    }
    with open(OUT_DIR / "feature_config.json", "w", encoding="utf-8") as f:
        json.dump(feature_config, f, ensure_ascii=False, indent=2)
    print(f"[INFO] saved {OUT_DIR / 'feature_config.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--labeling",
        type=str,
        default="auto",
        help="Labeling mode: 'auto' (default), 'absolute', or 'quantile'"
    )
    args = parser.parse_args()
    main(args)
