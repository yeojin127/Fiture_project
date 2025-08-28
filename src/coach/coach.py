# src/coach/coach.py
from typing import List, Tuple, Dict

# 변수명 → 팩터 키 매핑(방향은 '기대등급↑ = 나빠짐' 가정)
VAR_TO_FACTOR = {
    "SleepTime": "sleep_low",
    "Caffeine": "caffeine_high",
    "PhoneTime": "phone_high",
    "ActivityTime": "activity_low",
    "PM10": "pm_high",
    "MoodScore": "mood_low",
    "Temp": "temp_high",
    "Humidity": "humid_high",
}

def select_top3_factors_by_contrib(
    contribs: List[Tuple[str, float]],
    var_to_factor: Dict[str, str] = VAR_TO_FACTOR,
    k: int = 3
) -> List[str]:
    """
    SHAP 기반 (변수, penalty) 리스트를 받아 팩터 Top3를 뽑는다.
    - 동일 팩터 중복 제거
    - 상위 k개 반환
    """
    factors: List[str] = []
    seen = set()
    for var, _score in contribs:
        f = var_to_factor.get(var)
        if not f:
            continue
        if f not in seen:
            seen.add(f)
            factors.append(f)
        if len(factors) == k:
            break
    return factors
