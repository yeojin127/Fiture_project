import pandas as pd
import lightgbm as lgb
import numpy as np
from sklearn.model_selection import KFold, cross_val_score

# --- 설정 ---
# 교차검증 분할 개수 (K)
N_SPLITS = 5
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 데이터 경로
TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data/processed/train.csv")
VAL_DATA_PATH = os.path.join(PROJECT_ROOT, "data/processed/val.csv")


def cross_validate():
    print("--- LightGBM 모델 K-Fold 교차검증 시작 ---")

    # 1. 전체 학습 데이터 구성 (train + val)
    try:
        train_df = pd.read_csv(TRAIN_DATA_PATH)
        val_df = pd.read_csv(VAL_DATA_PATH)
        # 두 데이터프레임을 하나로 합침
        full_train_df = pd.concat([train_df, val_df], ignore_index=True)
        print("전체 학습 데이터 구성 완료.")
    except FileNotFoundError as e:
        print(f"[오류] 데이터 파일을 찾을 수 없습니다: {e.filename}")
        return

    # 2. 데이터 전처리
    X = full_train_df.drop("ConditionLabel", axis=1)
    y = full_train_df["ConditionLabel"]

    X_dummies = pd.get_dummies(X)
    print("데이터 전처리 완료.")

    # 3. 모델 정의
    model = lgb.LGBMClassifier(random_state=42)

    # 4. K-Fold 교차검증 설정
    # 데이터를 5개로 나누고, 섞어서 사용
    kfold = KFold(n_splits=N_SPLITS, shuffle=True, random_state=42)

    # 5. 교차검증 실행 및 평가
    print(f"\n--- {N_SPLITS}-Fold 교차검증을 수행합니다 ---")

    # 5-1. 정확도(Accuracy) 계산
    # cross_val_score는 각 Fold의 점수를 배열(array) 형태로 반환
    accuracy_scores = cross_val_score(model, X_dummies, y, cv=kfold, scoring='accuracy')

    print("\n[정확도 점수]")
    for i, score in enumerate(accuracy_scores):
        print(f"  Fold {i + 1}: {score:.4f}")
    print(f"▶ 평균 정확도: {np.mean(accuracy_scores):.4f} (표준편차: {np.std(accuracy_scores):.4f})")

    # 5-2. MAE(Mean Absolute Error) 계산
    # scikit-learn의 점수(score)는 높을수록 좋은 것을 가정하므로, MAE는 음수로 변환된 값을 사용
    mae_scores = cross_val_score(model, X_dummies, y, cv=kfold, scoring='neg_mean_absolute_error')
    mae_scores = -mae_scores  # 다시 양수로 변환

    print("\n[MAE 점수]")
    for i, score in enumerate(mae_scores):
        print(f"  Fold {i + 1}: {score:.4f}")
    print(f"▶ 평균 MAE: {np.mean(mae_scores):.4f} (표준편차: {np.std(mae_scores):.4f})")


if __name__ == "__main__":
    cross_validate()