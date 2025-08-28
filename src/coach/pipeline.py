# src/pipeline.py
from typing import Dict, List, Tuple, Optional
import numpy as np
import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from model_train.infer import load_model, predict_grade_and_proba
from model_train.shap_utils import build_explainer_for_expected_grade, shap_penalties_for_sample
from coach.coach import select_top3_factors_by_contrib
from coach.card_builder import get_library, build_card

class CoachPipeline:
    """
    모델 로드 → SHAP Explainer 준비 → 예측 → SHAP 기여도 → Top3 팩터 → 카드 생성
    한 번 만들어 놓고 UI나 CLI, API 어디서든 호출만 하면 됨.
    """
    def __init__(
        self,
        model_path: str,
        background_X: np.ndarray,
        feature_names: List[str],
        coach_rules_json: Optional[str] = None
    ):
        self.model = load_model(model_path)
        self.feature_names = feature_names
        self.explainer = build_explainer_for_expected_grade(self.model, background_X)
        self.lib = get_library(coach_rules_json)  # 없으면 기본 룰 사용

    def predict_card(self, X_row: np.ndarray) -> Dict:
        """
        X_row shape: (1, n_features)
        return: card dict (title, summary, reasons, actions, food, warnings)
        """
        # 1) 등급/확률
        grade, _proba = predict_grade_and_proba(self.model, X_row)

        # 2) SHAP 기대등급 기준 기여도(+ 방향만 감점으로)
        contribs: List[Tuple[str, float]] = shap_penalties_for_sample(
            self.explainer, X_row, self.feature_names
        )
        # 예: [("sleep_time", 0.31), ("phone_time", 0.12), ("temp", 0.08), ...]

        # 3) 변수→팩터 매핑 후 Top3
        top3_factors = select_top3_factors_by_contrib(contribs)
        # 예: ["sleep_low","phone_high","temp_high"]

        # 4) 환경값(경고용) 컨텍스트 구성
        ctx = {}
        for key in ("pm10", "temp", "humidity"):
            if key in self.feature_names:
                idx = self.feature_names.index(key)
                ctx[key] = float(X_row[0, idx])

        # 5) 카드 생성
        card = build_card(grade, top3_factors, self.lib, context_env=ctx, max_actions=5)
        return card
