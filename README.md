===

🌟 Fiture Project

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


## 📂 프로젝트 폴더 구조

# 📂 프로젝트 폴더 구조 (데이터 + 모델 학습 통합)

| 경로                          | 설명 |
| ----------------------------- | ------------------------------------------------ |
| **`config/`**                 | 합성 데이터 생성 및 학습 설정 |
| └── `life_profile.yaml`       | 6가지 생활 유형 정의 (weekend, deadline, caffeine 등) |
| **`data/raw/`**               | 원본 환경 데이터 |
| ├── `humidity.csv`            | 습도 데이터 |
| ├── `pm.csv`                  | 미세먼지(PM10) 데이터 |
| └── `temp.csv`                | 온도 데이터 |
| **`data/processed/`**         | 전처리/합성/라벨링 데이터 |
| ├── `env_merged.csv`          | 환경 데이터 병합 결과 |
| ├── `feature_config.json`     | 피처 정의 및 설명 |
| ├── `life_synth_merged.csv`   | 생활+환경 합성 데이터 (총 **6000행**) |
| ├── `synth_weekend.csv`       | 주말 보상수면형 합성 |
| ├── `synth_deadline.csv`      | 시험·마감 주간형 합성 |
| ├── `synth_caffeine.csv`      | 카페인 민감형 합성 |
| ├── `synth_owl_chrono.csv`    | 야행성(올빼미형) 합성 |
| ├── `synth_env_sens.csv`      | 환경 민감형 합성 |
| ├── `synth_weekday.csv`       | 평일 루틴형 합성 |
| ├── `train.csv`               | 학습 데이터 (**80%**) |
| ├── `val.csv`                 | 검증 데이터 (**10%**) |
| └── `test.csv`                | 최종 테스트 데이터 (**10%**) |
| **`src/`**                    | 주요 파이프라인 코드 |
| ├── `build_datasets.py`       | (선택) 전체 파이프라인 실행 스크립트 |
| ├── `merge_env.py`            | 환경 데이터 병합 (raw → env_merged.csv) |
| ├── `synth_merge.py`          | 프로파일 기반 합성 데이터 생성 |
| └── `label_split.py`          | 라벨링 및 train/val/test 분리 |
| **`src/ml/`**                 | 모델 학습 관련 모듈 |
| ├── `data.py`                 | 데이터 로드/전처리 |
| ├── `model.py`                | LightGBM 모델 정의 (monotone 제약 포함) |
| ├── `train.py`                | 학습 루프, 체크포인트 저장 |
| ├── `evaluate.py`             | 평가, 메트릭 계산, 혼동행렬 저장 |
| ├── `tune_optuna.py`          | Optuna 하이퍼파라미터 튜닝 |
| └── `export.py`               | ONNX 변환 → OpenVINO IR 내보내기 |
| **`models/`**                 | 학습된 모델 저장 |
| ├── `model_lgbm.txt`          | LightGBM 모델 파일 |
| ├── `model.pkl`               | Joblib 저장 모델 |
| ├── `model.onnx`              | ONNX 변환 결과 |
| └── `openvino_ir/`            | OpenVINO IR 파일 (xml, bin) |
| **`reports/`**                | 학습 결과 리포트 |
| ├── `metrics.json`            | 정확도 및 세부 메트릭 |
| ├── `confusion_matrix.png`    | 혼동행렬 시각화 |
| └── `optuna_best.txt`         | 하이퍼파라미터 튜닝 결과 |
| **`runs/`**                   | 실험별 로그/체크포인트 (자동 생성) |
| └── `2025-08-17_120000/`      | 예시: 날짜별 모델, 로그 저장 |
| **실행 스크립트**             | 학습/튜닝/평가 진입점 |
| ├── `train_model.py`          | 학습 실행 |
| ├── `tune_model.py`           | Optuna 튜닝 실행 |
| └── `evaluate_model.py`       | 평가 실행 |
| **`README.md`**               | 프로젝트 개요 및 설명 |




