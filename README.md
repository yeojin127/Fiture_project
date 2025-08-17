# Fiture Project

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

| 폴더 / 파일 | 설명 |
|-------------|------------------------------------------------|
| `config/`   | 설정 관련 파일 |
| └─ `life_profile.yaml` | 합성 데이터 생성 설정 |
| `data/raw/` | 원천 데이터 (환경 데이터: 미세먼지, 온도, 습도) |
| ├─ `humidity.csv` | 습도 데이터 |
| ├─ `pm.csv`       | 미세먼지 데이터 |
| └─ `temp.csv`     | 기온 데이터 |
| `data/processed/` | 전처리된 데이터 (학습 가능 형태) |
| ├─ `dataset_merged.csv` | 병합된 전체 데이터 |
| ├─ `dataset_ready.csv`  | 라벨링 완료 학습용 데이터 |
| ├─ `env_merged.csv`     | 환경 데이터 병합본 |
| ├─ `feature_config.json`| 특성(Feature) 설정 |
| ├─ `life_synth.csv`     | 합성 생활 데이터 |
| ├─ `train.csv`          | 학습 데이터 |
| └─ `valid.csv`          | 검증 데이터 |
| `models/`   | 학습된 모델 저장 |
| ├─ `model_lgbm.txt` | LightGBM 저장 모델 |
| ├─ `model.pkl`      | Joblib 저장 모델 |
| ├─ `model.onnx`     | ONNX 변환 결과 |
| └─ `openvino_ir/`   | OpenVINO IR (xml, bin) |
| `reports/`  | 학습 결과 리포트 |
| ├─ `metrics.json`        | 정확도, 메트릭 수치 |
| ├─ `confusion_matrix.png`| 혼동행렬 그래프 |
| └─ `optuna_best.txt`     | 하이퍼파라미터 튜닝 결과 |
| `runs/`     | 실험별 결과 저장 (자동 생성) |
| └─ `2025-08-17_120000/` | 예시: 날짜별 모델, 로그 |
| `ppt/`      | 발표 자료 |
| `src/`      | 주요 소스 코드 |
| ├─ `build_datasets.py`   | 데이터셋 빌드 |
| ├─ `condition_labeling.py`| 라벨링 스크립트 |
| ├─ `merge_env.py`        | 환경 데이터 병합 |
| ├─ `synthesize_life.py`  | 생활 데이터 합성 |
| └─ `ml/`                 | 모델 관련 모듈 |
| &nbsp;&nbsp;&nbsp;├─ `data.py`      | 데이터 로드/전처리 |
| &nbsp;&nbsp;&nbsp;├─ `model.py`     | LightGBM 모델 정의 |
| &nbsp;&nbsp;&nbsp;├─ `train.py`     | 학습 루프, 체크포인트 |
| &nbsp;&nbsp;&nbsp;├─ `evaluate.py`  | 평가, 혼동행렬 저장 |
| &nbsp;&nbsp;&nbsp;├─ `tune_optuna.py` | Optuna 튜닝 |
| &nbsp;&nbsp;&nbsp;└─ `export.py`    | ONNX → OpenVINO 변환 |
| `train_model.py`    | 학습 실행 진입점 |
| `tune_model.py`     | 튜닝 실행 진입점 |
| `evaluate_model.py` | 평가 실행 진입점 |
| `README.md`         | 프로젝트 개요 및 설명 |

