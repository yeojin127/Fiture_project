# src/train_model.py

import pandas as pd
import numpy as np # RMSE 계산을 위해 numpy 추가
import lightgbm as lgb
from sklearn.metrics import mean_squared_error # 회귀 모델 평가 지표
import matplotlib.pyplot as plt # 피처 중요도 시각화를 위해 추가

# 1. 데이터 불러오기
try:
    train_df = pd.read_csv('../data/processed/train.csv')
    valid_df = pd.read_csv('../data/processed/valid.csv')
    print("데이터 불러오기 성공!")
except FileNotFoundError:
    print("오류: train.csv 또는 valid.csv 파일을 찾을 수 없습니다.")
    print("파일 경로: '../data/processed/'를 확인해주세요.")
    exit() # 파일이 없으면 실행 중단

# 2. Feature와 Target 분리
# 목표 변수를 'MoodScore'로 설정
TARGET = 'MoodScore'

# Target 변수가 데이터에 있는지 확인
if TARGET not in train_df.columns:
    print(f"오류: 목표 변수인 '{TARGET}'가 데이터에 존재하지 않습니다.")
    exit()

X_train = train_df.drop(TARGET, axis=1)
y_train = train_df[TARGET]

X_valid = valid_df.drop(TARGET, axis=1)
y_valid = valid_df[TARGET]

print(f"\n학습 데이터 크기: {X_train.shape}")
print(f"검증 데이터 크기: {X_valid.shape}")

# 3. LightGBM 모델 학습
# 회귀 문제이므로 LGBMRegressor 사용
# n_estimators와 learning_rate 등 주요 파라미터를 설정하여 성능 향상 가능
lgbm = lgb.LGBMRegressor(
    objective='regression', # 회귀 목표 함수
    metric='rmse',          # 평가 지표로 Root Mean Squared Error 사용
    random_state=42
)

print("\n모델 학습을 시작합니다...")
lgbm.fit(X_train, y_train)
print("모델 학습 완료!")

# 4. 예측 및 평가
preds = lgbm.predict(X_valid)

# 회귀 모델의 성능은 RMSE(Root Mean Squared Error)로 평가하는 것이 일반적
# RMSE는 모델의 예측 오차를 나타내며, 낮을수록 좋습니다.
rmse = np.sqrt(mean_squared_error(y_valid, preds))
print(f"\n모델 예측 성능 (RMSE): {rmse:.4f}")

# 5. 피처 중요도 확인
# 어떤 변수가 MoodScore 예측에 가장 큰 영향을 미치는지 확인
print("\n피처 중요도:")
lgb.plot_importance(lgbm, max_num_features=10)
plt.title('Feature Importance')
plt.tight_layout() # 그래프 레이아웃 자동 조정
plt.show()
