import os
import pandas as pd
import lightgbm as lgb
import joblib
import subprocess
import sys
# [추가] hummingbird와 numpy를 import 합니다.
from hummingbird.ml import convert
import numpy as np
# [추가] 파일 이동을 위한 shutil 라이브러리
import shutil

# --- 설정 ---

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, "data/processed/train.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "data/models")
OPENVINO_DIR = os.path.join(MODELS_DIR, "openvino_ir")
LGBM_MODEL_PATH = os.path.join(MODELS_DIR, "model_lgbm.pkl")
# [수정] Hummingbird로 변환된 ONNX 파일 이름을 지정합니다.
ONNX_MODEL_PATH = os.path.join(MODELS_DIR, "model_lgbm_hb.onnx")

# --- 디렉토리 생성 ---
os.makedirs(OPENVINO_DIR, exist_ok=True)


def train_lightgbm():
    """1. LightGBM 모델 학습"""
    print("--- 1. LightGBM 모델 학습 시작 ---")

    df = pd.read_csv(TRAIN_DATA_PATH)
    X = df.drop("ConditionLabel", axis=1)
    y = df["ConditionLabel"]

    print("데이터 전처리(원-핫 인코딩)를 수행합니다...")
    X = pd.get_dummies(X)

    print(f"데이터 로드 및 전처리 완료. 피처 개수: {X.shape[1]}, 샘플 개수: {X.shape[0]}")

    model = lgb.LGBMClassifier(random_state=42)
    model.fit(X, y)
    print("모델 학습 완료.")

    joblib.dump(model, LGBM_MODEL_PATH)
    print(f"학습된 모델 저장 완료: {LGBM_MODEL_PATH}")

    return model, X.shape[1]


def convert_to_onnx(model, num_features):
    """2. 학습된 모델을 ONNX 형식으로 변환 (Hummingbird 사용)"""
    print("\n--- 2. ONNX 변환 시작 (Hummingbird 사용) ---")

    # Hummingbird 변환을 위한 더미(dummy) 입력 데이터 생성
    X_dummy = np.zeros((1, num_features), dtype=np.float32)

    # Hummingbird를 사용하여 모델을 ONNX로 변환
    # extra_config={'onnx_target_opset': 13} 옵션을 추가하여 opset 버전을 지정합니다.
    onnx_model = convert(model, backend="onnx", test_input=X_dummy, extra_config={'onnx_target_opset': 13}).model

    # 변환된 ONNX 모델을 파일에 저장
    with open(ONNX_MODEL_PATH, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"ONNX 모델 저장 완료: {ONNX_MODEL_PATH}")


def convert_to_openvino():
    """3. ONNX 모델을 OpenVINO IR 형식으로 변환"""
    print("\n--- 3. OpenVINO IR 변환 시작 ---")

    # --output 옵션을 제거하여 현재 폴더에 IR 파일을 생성
    command = ["ovc", ONNX_MODEL_PATH]
    print(f"실행 명령어: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("OpenVINO IR 변환 성공!")
        print(result.stdout)

        # 변환 성공 후, 생성된 IR 파일들을 목표 폴더로 이동
        print(f"생성된 IR 파일들을 '{OPENVINO_DIR}' 폴더로 이동합니다...")
        base_name = os.path.splitext(os.path.basename(ONNX_MODEL_PATH))[0]
        xml_file = base_name + ".xml"
        bin_file = base_name + ".bin"

        shutil.move(xml_file, os.path.join(OPENVINO_DIR, xml_file))
        shutil.move(bin_file, os.path.join(OPENVINO_DIR, bin_file))
        print("파일 이동 완료.")

    except subprocess.CalledProcessError as e:
        print("오류: OpenVINO IR 변환 중 에러가 발생했습니다.")
        print(e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    lgbm_model, feature_count = train_lightgbm()
    convert_to_onnx(lgbm_model, feature_count)
    convert_to_openvino()

    print("\n🎉 모든 파이프라인 작업이 성공적으로 완료되었습니다!")