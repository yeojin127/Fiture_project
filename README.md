
# 🌟 Fiture Project

사용자의 생활·환경 데이터를 바탕으로 **다음날 컨디션을 예측**하고,  
맞춤형 팁·가이드를 제공하여 건강한 생활 습관 형성을 돕는 프로젝트입니다

---


## 🚀 주요 기능
1. **데이터 수집 및 합성**  
   - 생활 데이터 합성 (수면, 기분, 활동량, 카페인 등)  
   - 환경 데이터 수집 및 병합 (온도, 습도, 미세먼지 등)

2. **데이터 전처리 및 라벨링**  
   - 결측치 처리, 범위 정규화  
   - 컨디션 점수 산출 및 등급 라벨링

3. **모델 학습 및 예측**  
   - LightGBM 기반 분류 모델 학습  
   - OpenVINO 최적화 및 추론 성능 향상

4. **UI 구현 (PySide6)**  
   - 사용자 입력창 및 예측 결과 시각화  
   - 생활 개선 팁 및 맞춤형 가이드 제공

---

## 🎯 목표
- ±1 등급 기준 90% 이상의 예측 정확도
- 개인 맞춤형 생활 개선 가이드 제공
- 데이터 기반 자기 관리 습관 형성 지원

---

## 📂 프로젝트 폴더 구조 (데이터 + 모델 학습 통합)


| 경로 | 설명 |
|------|------|
| **config/** | 합성 데이터 생성 및 학습 설정 |
| └── life_profile.yaml | 6가지 생활 유형 정의 (weekend, deadline, caffeine 등) |
| **data/** | 데이터 저장소 |
| ├── raw/ | 원본 환경 데이터 (온도, 습도, PM 등) |
| │   ├── humidity.csv | 습도 데이터 |
| │   ├── pm.csv | 미세먼지(PM10) 데이터 |
| │   └── temp.csv | 온도 데이터 |
| ├── processed/ | 전처리/합성/라벨링 데이터 |
| │   ├── env_merged.csv | 환경 데이터 병합 결과 |
| │   ├── feature_config.json | 피처 정의 및 설명 |
| │   ├── life_synth_merged.csv | 생활+환경 합성 데이터 (총 6000행) |
| │   ├── synth_*.csv | 생활 유형별 합성 데이터 (weekend, deadline, caffeine 등) |
| │   ├── train.csv | 학습 데이터 (80%) |
| │   ├── val.csv | 검증 데이터 (10%) |
| │   └── test.csv | 최종 테스트 데이터 (10%) |
| └── models/ | 학습된 모델 및 추론용 파일 |
|     ├── model_lgbm.txt | LightGBM 모델 파일 |
|     ├── model.pkl | Joblib 저장 모델 |
|     ├── model.onnx | ONNX 변환 결과 |
|     └── openvino_ir/ | OpenVINO IR (xml, bin) |
| **src/** | 주요 파이프라인 코드 |
| ├── labeling/ | 전처리 및 라벨링 |
| │   ├── preprocess.py | 전처리/병합 함수 |
| │   └── label_split.py | 라벨링 + train/val/test 분리 |
| ├── model_train/ | 학습 및 추론 |
| │   ├── train.py | 모델 학습 |
| │   ├── infer.py | LightGBM + OpenVINO 추론 |
| │   ├── shap_utils.py | SHAP 기여도 해석 |
| │   └── tune_optuna.py | Optuna 하이퍼파라미터 튜닝 |
| ├── coach/ | 피드백 로직 (feedback) |
| │   ├── coach.py | Top3 팩터 선정 + 행동 추천 |
| │   └── card_builder.py | build_card 함수 (등급/행동/음식/경고 조합) |
| └── ui/ | 사용자 인터페이스 |
|     ├── main_ui.py | PySide6 앱 실행 |
|     └── components.py | 카드 위젯 등 UI 컴포넌트 |
| **reports/** | 학습 결과 리포트 |
| ├── metrics.json | 정확도 및 메트릭 |
| ├── confusion_matrix.png | 혼동행렬 |
| └── optuna_best.txt | 최적 하이퍼파라미터 |
| **tests/** | 단위 테스트 |
| └── test_coach.py | coach 모듈 테스트 |
| **`README.md`**               | 프로젝트 개요 및 설명 |




