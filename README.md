Fiture_project/
│
├── config/                # 프로젝트 설정 파일 모음
│   ├── feature_config.json # 라벨링된 데이터의 피처 정보, 컷팅 규칙, 데이터 분할 설정 등이 저장됨
│   └── 기타 설정 파일들…
│
├── data/                   # 데이터 저장소
│   ├── raw/                # 원본 데이터 (환경 데이터 CSV, 합성 생활 데이터 CSV)
│   ├── processed/          # 전처리·라벨링 후 저장된 데이터
│   │   ├── dataset_ready.csv # 모든 피처+라벨 포함한 최종 데이터셋
│   │   ├── train.csv         # 학습용 데이터(80%)
│   │   ├── valid.csv         # 검증용 데이터(20%)
│   │   └── feature_config.json # src에서 생성한 피처 정보 JSON (config에도 복사 가능)
│   └── external/            # (필요시) 외부 수집 API 결과나 추가 데이터
│
├── src/                    # Python 소스 코드
│   ├── synthesize_life.py   # 생활 데이터 합성 생성기 (수면시간·활동시간·기분점수 등 가짜 데이터 만들기)
│   ├── merge_env_data.py    # 환경 데이터(PM10, 온도, 습도) 병합 코드
│   ├── condition_labeling.py# 환경+생활+MoodScore → ConditionScore 계산 후 등급 라벨링
│   ├── utils.py             # 데이터 전처리·유틸 함수 모음 (결측치 처리, 컬럼 변환 등)
│   └── train_model.py       # (추가 예정) LightGBM 등 모델 학습 코드
│
├── README.md               # 프로젝트 개요, 폴더 구조, 실행 방법
└── requirements.txt        # 필요한 파이썬 라이브러리 목록
