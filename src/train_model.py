# src/train_model.py

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import joblib
import optuna

# --- 1. 데이터 불러오기 ---
try:
    train_df = pd.read_csv('data/processed/train.csv')
    valid_df = pd.read_csv('data/processed/valid.csv')
    print("데이터 불러오기 성공!")
except FileNotFoundError:
    print("오류: train.csv 또는 valid.csv 파일을 찾을 수 없습니다.")
    exit()

# --- 2. Feature와 Target 분리 ---
TARGET = 'MoodScore'
if TARGET not in train_df.columns:
    print(f"오류: 목표 변수인 '{TARGET}'가 데이터에 존재하지 않습니다.")
    exit()

X_train = train_df.drop(TARGET, axis=1)
y_train = train_df[TARGET]
X_valid = valid_df.drop(TARGET, axis=1)
y_valid = valid_df[TARGET]

print(f"\n학습 데이터 크기: {X_train.shape}")
print(f"검증 데이터 크기: {X_valid.shape}")

# --- 3. Optuna를 사용한 하이퍼파라미터 튜닝 ---
print("\nOptuna를 사용한 하이퍼파라미터 튜닝을 시작합니다...")


def objective(trial):
    params = {
        'objective': 'regression_l1',
        'metric': 'rmse',
        'random_state': 42,
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'learning_rate': trial.suggest_float('learning_rate', 1e-3, 1e-1, log=True),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'num_leaves': trial.suggest_int('num_leaves', 20, 100),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
    }

    model = lgb.LGBMRegressor(**params)

    
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)],
              callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)])

    preds = model.predict(X_valid)
    rmse = np.sqrt(mean_squared_error(y_valid, preds))

    return rmse


# Optuna 스터디 생성 및 최적화 시작
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=500)

print(f"\n최적의 하이퍼파라미터: {study.best_params}")
print(f"최적 파라미터 사용 시 달성한 RMSE: {study.best_value:.4f}")

# --- 4. 최적 모델로 평가 및 저장 ---
best_params = study.best_params
final_model = lgb.LGBMRegressor(**best_params, random_state=42)
final_model.fit(X_train, y_train)

preds = final_model.predict(X_valid)
final_rmse = np.sqrt(mean_squared_error(y_valid, preds))
print(f"\n최종 모델 예측 성능 (RMSE): {final_rmse:.4f}")

model_filename = 'lgbm_mood_model_optuna.pkl'
joblib.dump(final_model, model_filename)
print(f"\n학습된 모델을 '{model_filename}' 파일로 저장했습니다.")

# --- 5. 피처 중요도 확인 ---
print("\n피처 중요도:")
lgb.plot_importance(final_model, max_num_features=10)
plt.title('Feature Importance')
plt.tight_layout()
plt.show()