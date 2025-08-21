# src/coach/card_builder.py
from typing import Dict, List, Any, Optional
import json
import os

# 기본 요약 문구
DEFAULT_GRADE_SUMMARY = {
    "1": "오늘의 컨디션은 최상! 유지가 포인트",
    "2": "좋은 컨디션! 조금의 변화로 컨디션을 최고로 만들어봐요.",
    "3": "균형이 필요해요. 컨디션을 위한 노력 필수!",
    "4": "충전이 필요한 날이네요. 자신을 위해 피드백을 실천해봅시다!.",
    "5": "완전 휴식 모드 필요! 오늘 하루쯤은 쉬는게 어떨까요?"
}

# 랭크별 행동 팁 (필요 최소만 넣음: 프로젝트에 맞춰 확장 가능)
DEFAULT_RULES_RANKED = {
    "sleep_low": {
        "rank1": ["오늘 낮잠 20분", "카페인 총 1잔 이내", "23:00 취침 알람 설정"],
        "rank2": ["자기 전 30분 스크린 OFF", "물 2잔 추가"],
        "rank3": ["취침시간 15분 앞당기기"]
    },
    "caffeine_high": {
        "rank1": ["오후 무카페인 전환", "총 1잔 제한", "디카페/보리차 대체"],
        "rank2": ["총 2잔 이내", "물 2잔 추가"],
        "rank3": ["진한 음료 희석해서 마시기"]
    },
    "phone_high": {
        "rank1": ["취침 1시간 전 폰 금지", "SNS 30분 타이머 설정", "블루라이트 필터 ON"],
        "rank2": ["알림 끄기(메신저 제외)", "스크롤 10분 제한"],
        "rank3": ["취침 전 10분 독서/명상으로 대체"]
    },
    "activity_low": {
        "rank1": ["10분 걷기 ×3(아·점·저)", "계단 사용", "전신 스트레칭 10분"],
        "rank2": ["점심 15분 산책", "1~2층 계단 오르기"],
        "rank3": ["집안 1000보 스텝"]
    },
    "pm_high": {
        "rank1": ["실내 운동", "KF마스크 착용", "귀가 후 세안/가글"],
        "rank2": ["물 2잔 추가", "환기는 짧게"],
        "rank3": ["외출 시 실내 동선 선택"]
    },
    "mood_low": {
        "rank1": ["감정일기 5분 쓰기", "친구·가족과 통화", "짧은 산책"],
        "rank2": ["좋아하는 음악 10분 듣기", "간단한 취미활동"],
        "rank3": ["깊게 호흡 3회"]
    },
    "temp_high": {
        "rank1": ["한낮 외출 자제", "전해질 보충", "헐렁한 옷차림"],
        "rank2": ["그늘 동선 선택", "수분 2잔 추가"],
        "rank3": ["선풍기/환기 짧게"]
    },
    "humidity_high": {
        "rank1": ["통풍·제습기 가동", "면 소재 옷 착용", "땀 식히기 주의"],
        "rank2": ["샤워 후 완전 건조", "양말 교체"],
        "rank3": ["끈적일 땐 미온수 세안"]
    }
}

# 음식 추천
DEFAULT_FOODS = {
    "default": {
        "morning": ["현미밥+달걀", "그릭요거트+바나나"],
        "snack": ["견과류 한 줌", "키위/오렌지"],
        "dinner": ["두부덮밥", "닭가슴살샐러드+맑은 국"]
    },
    "grade4_5": {
        "morning": ["누룽지/죽", "바나나"],
        "snack": ["플레인요거트", "과일 한 컵"],
        "dinner": ["맑은 미역국", "삶은 감자+채소무침"]
    }
}

def load_rules_from_json(json_path: str) -> Dict[str, Any]:
    """
    coach_rules.json 구조 예시:
    {
      "grade_summary": {...},
      "factor_rules_ranked": {...},
      "foods": {...}
    }
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_library(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    JSON이 있으면 덮어쓰기, 없으면 기본값 사용
    """
    lib = {
        "grade_summary": DEFAULT_GRADE_SUMMARY,
        "factor_rules_ranked": DEFAULT_RULES_RANKED,
        "foods": DEFAULT_FOODS
    }
    if config_path and os.path.exists(config_path):
        ext = load_rules_from_json(config_path)
        for k in ["grade_summary", "factor_rules_ranked", "foods"]:
            if k in ext:
                lib[k] = ext[k]
    return lib

def select_ranked_actions(
    top3_factors: List[str],
    rules_ranked: Dict[str, Dict[str, List[str]]],
    max_actions: int = 5
) -> List[str]:
    """
    1위→rank1, 2위→rank2, 3위→rank3 묶음에서 행동을 합쳐 노출
    """
    rank_keys = ["rank1", "rank2", "rank3"]
    actions: List[str] = []
    for i, factor in enumerate(top3_factors[:3]):
        cand = rules_ranked.get(factor, {}).get(rank_keys[i], [])
        for a in cand:
            if a not in actions:
                actions.append(a)
        if len(actions) >= max_actions:
            break
    return actions[:max_actions] if actions else ["물 6~8잔 마시기", "10분 스트레칭", "23:30 취침"]

def pick_foods(grade: int, foods: Dict[str, Dict[str, List[str]]]):
    key = "grade4_5" if grade in (4, 5) else "default"
    fm = foods[key]["morning"][0]
    fs = foods[key]["snack"][0]
    fd = foods[key]["dinner"][0]
    return fm, fs, fd

def build_card(
    grade: int,
    top3_factors: List[str],
    lib: Dict[str, Any],
    context_env: Optional[Dict[str, float]] = None,
    max_actions: int = 5
) -> Dict[str, Any]:
    summary = lib["grade_summary"][str(grade)]
    actions = select_ranked_actions(top3_factors, lib["factor_rules_ranked"], max_actions=max_actions)
    fm, fs, fd = pick_foods(grade, lib["foods"])

    warnings: List[str] = []
    if context_env:
        pm = context_env.get("pm10")
        temp = context_env.get("temp")
        humid = context_env.get("humidity")
        if pm is not None and pm > 80:
            warnings.append("미세먼지 높음: 실내 운동, 마스크 착용")
        if temp is not None and temp > 30:
            warnings.append("더위 주의: 한낮 외출 줄이고 수분 보충")
        if humid is not None and humid < 30:
            warnings.append("건조 주의: 가습 40~60% 유지")

    return {
        "title": f"오늘의 컨디션 {grade}/5",
        "summary": summary,
        "reasons": top3_factors,
        "actions": actions,
        "food": {"morning": fm, "snack": fs, "dinner": fd},
        "warnings": warnings
    }
