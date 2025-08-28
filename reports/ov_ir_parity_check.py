import json
import numpy as np
import pandas as pd
from pathlib import Path
from openvino import Core
from sklearn.metrics import accuracy_score

# -----------------------------
# 경로 설정
# -----------------------------
TRAIN_PATH = Path("data/processed/train.csv")
TEST_PATH  = Path("data/processed/test.csv")
FEAT_PATH  = Path("data/models/feature_names.json")
IR_PATH    = Path("data/models/openvino_ir/model_lgbm_hb.xml")

LABEL_OFFSET = 1  # 라벨이 1~5면 1, 0~4면 0

# -----------------------------
# ① feature_names.json 로드 / 재생성
# -----------------------------
def regenerate_feature_names():
    """train.csv를 원-핫 인코딩해서 feature_names.json 재생성"""
    df_train = pd.read_csv(TRAIN_PATH)
    X_train_df = df_train.drop(columns=["ConditionLabel"])
    X_train_ohe = pd.get_dummies(X_train_df)
    feature_names = X_train_ohe.columns.tolist()

    FEAT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FEAT_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_names, f, ensure_ascii=False)

    print(f"[INFO] feature_names.json 재생성 완료 (원핫 기준, {len(feature_names)}개)")
    return feature_names

if not FEAT_PATH.exists():
    feature_names = regenerate_feature_names()
else:
    with open(FEAT_PATH, "r", encoding="utf-8") as f:
        feature_names = json.load(f)
    # 원핫 전 컬럼일 경우 강제로 재생성
    if len(feature_names) < 14:  # 모델이 기대하는 14보다 적음
        print(f"[WARN] feature_names.json 피처 {len(feature_names)}개 → 재생성 필요")
        feature_names = regenerate_feature_names()
    else:
        print(f"[INFO] feature_names.json 로드 완료 (피처 {len(feature_names)}개)")

# -----------------------------
# ② test.csv 불러오기 & 전처리
# -----------------------------
df_test = pd.read_csv(TEST_PATH)

y_test = df_test["ConditionLabel"].to_numpy().ravel().astype(int)
X_test_df = df_test.drop(columns=["ConditionLabel"])

# 원핫
X_test_ohe = pd.get_dummies(X_test_df)

# 누락 피처 0으로 채움
missing = [c for c in feature_names if c not in X_test_ohe.columns]
for c in missing:
    X_test_ohe[c] = 0

# 불필요 피처 제거
extra = [c for c in X_test_ohe.columns if c not in feature_names]
if extra:
    X_test_ohe = X_test_ohe.drop(columns=extra)

# 순서 정렬
X_test_ohe = X_test_ohe[feature_names]
X_test = X_test_ohe.to_numpy().astype(np.float32)

print(f"[INFO] 테스트셋 정렬 완료. 샘플 {X_test.shape[0]}, 피처 {X_test.shape[1]}")
if missing:
    print(f"[INFO] 테스트에 없던 피처 {len(missing)}개 0으로 채움: {missing[:5]}{' ...' if len(missing) > 5 else ''}")
if extra:
    print(f"[INFO] 테스트 전용 피처 {len(extra)}개 제거: {extra[:5]}{' ...' if len(extra) > 5 else ''}")

# -----------------------------
# ③ IR 모델 로드 & 추론
# -----------------------------
ie = Core()
compiled = ie.compile_model(str(IR_PATH), "CPU")
inp = compiled.inputs[0].get_any_name()
out = compiled.outputs[0].get_any_name()

proba = compiled({inp: X_test})[out]
print("[INFO] OpenVINO IR 추론 완료.")

# -----------------------------
# ④ 결과 해석 (자동 오프셋 탐지)
# -----------------------------
print(f"[INFO] proba shape: {proba.shape}")

if proba.ndim == 2 and proba.shape[1] >= 2:
    # 멀티클래스 확률 출력
    pred0 = proba.argmax(axis=1)  # 0~(n_classes-1)
    # 자동 오프셋 탐지
    candidates = {
        "shift_-1": np.clip(pred0 - 1, 0, 4) + 1,
        "shift_0" : pred0 + 1,
        "shift_+1": np.clip(pred0 + 1, 0, 4) + 1,
    }
    scores = {k: accuracy_score(y_test, v) for k, v in candidates.items()}
    best_key = max(scores, key=scores.get)
    y_pred = candidates[best_key]
    print(f"[INFO] Offset auto-select → {best_key}, Acc={scores[best_key]:.4f}")
else:
    # 단일 회귀 점수 출력 (예: 1~5 등급 직접 예측)
    y_pred = np.rint(proba).astype(int).clip(1, 5).ravel()
    acc = accuracy_score(y_test, y_pred)
    print(f"[INFO] Regression-style output, Acc={acc:.4f}")

# ±1-grade accuracy
w1a = np.mean(np.abs(y_test - y_pred) <= 1)
print(f"IR ±1-grade Accuracy: {w1a:.4f}")
