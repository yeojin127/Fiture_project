import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, mean_absolute_error
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np

# --- 설정 ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 1. 평가할 모델 파일 경로를 LogisticRegression 모델로 지정
MODEL_PATH = os.path.join(PROJECT_ROOT, "data/models/model_lgbm.pkl")

# 2. 검증할 데이터 경로를 val.csv로 지정
DATA_PATH = os.path.join(PROJECT_ROOT, "data/processed/val.csv")

# 3. 학습 데이터 경로는 컬럼 정렬을 위해 필요
TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data/processed/train.csv")

# 4. 결과를 저장할 폴더 경로
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def evaluate():
    print(f"--- 모델 검증 시작: {MODEL_PATH} ---")
    print(f"--- 검증 데이터: {DATA_PATH} ---")

    # 모델 불러오기
    try:
        model = joblib.load(MODEL_PATH)
        print("모델 불러오기 성공.")
    except FileNotFoundError:
        print(f"[오류] 모델 파일을 찾을 수 없습니다: {MODEL_PATH}")
        return

    # 데이터 불러오기
    try:
        train_df = pd.read_csv(TRAIN_DATA_PATH)
        val_df = pd.read_csv(DATA_PATH)
        print("학습 및 검증 데이터 불러오기 성공.")
    except FileNotFoundError as e:
        print(f"[오류] 데이터 파일을 찾을 수 없습니다: {e.filename}")
        return

    # 데이터 전처리 (학습 데이터와 동일하게)
    print("검증 데이터 전처리를 수행합니다...")
    X_train = train_df.drop("ConditionLabel", axis=1)
    X_val = val_df.drop("ConditionLabel", axis=1)
    y_val = val_df["ConditionLabel"]

    X_train_dummies = pd.get_dummies(X_train)
    X_val_dummies = pd.get_dummies(X_val)

    # 학습 데이터에 있는 컬럼을 기준으로 검증 데이터의 컬럼을 맞춤
    X_val_aligned = X_val_dummies.reindex(columns=X_train_dummies.columns, fill_value=0)

    print("데이터 전처리 완료.")

    # 예측 수행
    print("예측을 수행합니다...")
    predictions = model.predict(X_val_aligned)

    # 성능 평가 및 출력
    print("\n--- 모델 검증 결과 ---")

    accuracy = accuracy_score(y_val, predictions)
    print(f"\n✅ 정확도 (Accuracy): {accuracy:.4f}")

    mae = mean_absolute_error(y_val, predictions)
    print(f"✅ MAE (평균 절대 오차): {mae:.4f}")

    within_one_accuracy = np.mean(np.abs(y_val - predictions) <= 1)
    print(f"✅ ±1 등급 정확도: {within_one_accuracy:.4f} ({within_one_accuracy:.2%})")

    print("\n✅ 상세 보고서 (Classification Report):")
    print(classification_report(y_val, predictions, zero_division=0))

    print("\n✅ 혼동 행렬(Confusion Matrix) 이미지를 생성합니다...")
    cm = confusion_matrix(y_val, predictions)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix (Validation)')

    # reports 폴더에 이미지 저장
    confusion_matrix_path = os.path.join(REPORTS_DIR, "confusion_matrix_validation.png")
    plt.savefig(confusion_matrix_path)
    print(f"혼동 행렬 이미지가 '{confusion_matrix_path}'에 저장되었습니다.")


if __name__ == "__main__":
    evaluate()