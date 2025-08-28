import numpy as np
import pandas as pd
from openvino.runtime import Core
from sklearn.metrics import accuracy_score

# ① 데이터 로드 및 전처리 (run_pipeline_lgbm.py와 동일하게)
# 원본 test.csv를 불러와서 학습 시 사용했던 전처리를 재현
df_test = pd.read_csv("data/processed/test.csv")

# y_test (실제 정답 라벨)는 "ConditionLabel" 열
y_test = df_test["ConditionLabel"].to_numpy().ravel().astype(int)

# X_test (모델 입력)는 "ConditionLabel" 열을 제외한 모든 열
X_test = df_test.drop("ConditionLabel", axis=1)

# 학습 시 사용했던 원-핫 인코딩(get_dummies)을 test 데이터에도 동일하게 적용
X_test = pd.get_dummies(X_test)
# OpenVINO 모델 입력 형식에 맞게 데이터 타입 변환
X_test = X_test.to_numpy().astype(np.float32)

print(f"테스트 데이터 전처리 완료. 피처 개수: {X_test.shape[1]}, 샘플 개수: {X_test.shape[0]}")

# ② IR 로드 & 추론
# 수정된 추론 부분 (오류 해결)
try:
    ie = Core()
    compiled = ie.compile_model("data/models/openvino_ir/model_lgbm_hb.xml", "CPU")
    inp = compiled.inputs[0].get_any_name()
    out = compiled.outputs[0].get_any_name()

    # 입력 딕셔너리 생성
    input_dict = {inp: X_test}

    # compiled 객체에 직접 딕셔너리를 전달하여 추론 수행
    result = compiled(input_dict)

    # 결과를 out 변수를 키로 사용하여 가져옴
    proba = result[out]

    print("OpenVINO IR 추론 완료.")

except Exception as e:
    print(f"OpenVINO 추론 중 오류가 발생했습니다: {e}")
    exit()

# ③ 출력 해석 (확률/로짓 → 클래스)
if proba.ndim == 2 and proba.shape[1] >= 2:
    y_pred = proba.argmax(axis=1) + 1  # 라벨을 1~5로 사용 중이면 +1
else:
    # 회귀형 등급 점수라면 반올림 후 1~5로 클립
    y_pred = np.rint(proba).astype(int).clip(1,5).ravel()

# ④ 지표 계산
acc = accuracy_score(y_test, y_pred)
w1a = np.mean(np.abs(y_test - y_pred) <= 1)  # ±1등급 정확도
print(f"\nIR Accuracy: {acc:.4f}")
print(f"IR ±1-grade Accuracy: {w1a:.4f}")