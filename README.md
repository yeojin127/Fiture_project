\## 목적

\- 미세먼지/기온/습도(500일) + 생활 데이터(합성) 결합

\- 라벨(컨디션 등급) 생성 → LightGBM 학습 전처리 완료



\## 폴더 구조(제안)

data/

&nbsp; raw/            # 원본 CSV (pm.csv, temp.csv, humidity.csv)

&nbsp; processed/      # 전처리/결합 결과

notebooks/

&nbsp; 01\_merge\_env.ipynb

&nbsp; 02\_synthesize\_life.ipynb

src/

&nbsp; merge\_env.py

&nbsp; synth\_life.py

&nbsp; build\_dataset.py



\## 실행 순서(요약)

1\) 환경데이터 병합(날짜 기준)  

2\) 생활데이터 합성 생성  

3\) 환경+생활 결합 후 라벨 생성  

4\) 모델 학습 단계로 전달



