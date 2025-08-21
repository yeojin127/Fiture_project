# src/model/infer.py
from typing import Tuple, List, Optional
import numpy as np
import joblib

def load_model(model_path: str):
    """학습된 LightGBM/Sklearn 모델 로드"""
    return joblib.load(model_path)

def predict_grade_and_proba(model, X: np.ndarray, classes: Optional[List[int]] = None) -> Tuple[int, np.ndarray]:
    """
    모델로 등급(정수)과 각 등급 확률 반환
    - classes 미지정 시 [1,2,3,4,5]로 가정
    """
    if classes is None:
        classes = [1, 2, 3, 4, 5]

    proba = model.predict_proba(X)  # shape: (n, n_classes)
    pred_idx = np.argmax(proba, axis=1)[0]
    pred_grade = classes[pred_idx]
    return pred_grade, proba[0]
