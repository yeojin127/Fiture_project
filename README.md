🎯 목적

환경 데이터(미세먼지·기온·습도, 500일) + 합성 생활 데이터 결합

라벨(컨디션 등급) 생성 → LightGBM 학습 전처리 완료

📂 폴더 구조
경로	설명
config/	합성 데이터 생성 프로파일 설정
└── life_profile.yaml	6가지 생활 유형 정의 (weekend, deadline, caffeine 등)
data/raw/	원본 환경 데이터
├── humidity.csv	습도 데이터
├── pm.csv	미세먼지(PM10) 데이터
└── temp.csv	온도 데이터
data/processed/	전처리/합성/라벨링 데이터
├── env_merged.csv	환경 데이터 병합 결과
├── feature_config.json	피처 정의 및 설명
├── life_synth_merged.csv	생활+환경 합성 데이터 (총 6000행)
├── synth_weekend.csv	주말 보상수면형 합성
├── synth_deadline.csv	시험·마감 주간형 합성
├── synth_caffeine.csv	카페인 민감형 합성
├── synth_owl_chrono.csv	야행성(올빼미형) 합성
├── synth_env_sens.csv	환경 민감형 합성
├── synth_weekday.csv	평일 루틴형 합성
├── train.csv	학습 데이터 (80%)
├── val.csv	검증 데이터 (10%)
└── test.csv	최종 테스트 데이터 (10%)
src/	주요 파이프라인 코드
├── build_datasets.py	(선택) 전체 파이프라인 실행 스크립트
├── merge_env.py	환경 데이터 병합 (raw → env_merged.csv)
├── synth_merge.py	프로파일 기반 합성 데이터 생성
└── label_split.py	라벨링 및 train/val/test 분리


⚡ 실행 순서 (Pipeline)

1️⃣ 환경 데이터 병합 → merge_env.py
2️⃣ 생활 데이터 합성 생성 → synth_merge.py
3️⃣ 환경+생활 데이터 결합 & 라벨링 → label_split.py
4️⃣ Train/Val/Test 분할 → 모델 학습 단계 전달

flowchart TD
    A[Raw 환경데이터] -->|merge_env.py| B[env_merged.csv]
    B -->|synth_merge.py| C[생활 합성 데이터]
    C -->|label_split.py| D[(train/val/test)]
    D --> E[LightGBM 학습]
