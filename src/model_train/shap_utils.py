# src/model/shap_utils.py
from typing import Dict, List, Tuple
import numpy as np
import shap

def expected_grade_proba(model, X: np.ndarray) -> np.ndarray:
    """
    기대등급 E[grade] = sum_k k * P(class=k)
    classes = [1,2,3,4,5] 가정
    """
    P = model.predict_proba(X)  # (n, 5)
    classes = np.arange(1, P.shape[1] + 1)  # [1..5]
    return (P * classes).sum(axis=1)

def build_explainer_for_expected_grade(model, background_X: np.ndarray):
    """
    기대등급 함수를 대상으로 SHAP Explainer 구성
    """
    f = lambda X: expected_grade_proba(model, X)
    explainer = shap.Explainer(f, background_X)
    return explainer

def shap_penalties_for_sample(
    explainer,
    X_row: np.ndarray,
    feature_names: List[str]
) -> List[Tuple[str, float]]:
    """
    단일 샘플(X_row shape: (1, n_features))의 '감점 기여도' Top 변수 반환
    - 기대등급을 '올리는' 방향(=나빠지는 쪽) 기여만 penalty로 사용
    - 양수만 취하고 크기순 정렬
    """
    phi = explainer(X_row)  # shap values for expected grade
    vals = np.asarray(phi.values)[0]  # (n_features,)
    penalties = np.maximum(0.0, vals)

    pairs = [(feature_names[i], float(penalties[i])) for i in range(len(feature_names)) if penalties[i] > 0]
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs  # [(var, penalty), ...]
