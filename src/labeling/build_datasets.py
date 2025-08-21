import pandas as pd
from pathlib import Path

OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

def read_csv_safely(path, **kwargs):
    try:
        return pd.read_csv(path, **kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949", **kwargs)

def normalize_date_col(df, col="date"):
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = pd.to_datetime(df[col].astype(str), format="%Y%m%d", errors="coerce")
    else:
        df[col] = pd.to_datetime(df[col].astype(str).str.strip(), errors="coerce")
    df.dropna(subset=[col], inplace=True)
    return df

def merge_env_and_life(env_path="data/processed/env_merged.csv",
                       life_path="data/processed/life_synth.csv",
                       out_path="data/processed/dataset_merged.csv"):
    # 1) 환경 데이터 읽기
    if not Path(env_path).exists():
        raise FileNotFoundError(f"환경 파일을 찾을 수 없음: {env_path}")
    env = read_csv_safely(env_path)

    # region 컬럼 제거
    if "region" in env.columns:
        env = env.drop(columns=["region"])

    # 날짜 처리
    if "date" not in env.columns:
        start = pd.Timestamp.today().normalize() - pd.Timedelta(days=len(env)-1)
        env["date"] = pd.date_range(start, periods=len(env), freq="D")

    env = normalize_date_col(env, "date")
    env = env.sort_values("date").reset_index(drop=True)

    # 2) 생활 데이터 읽기
    if not Path(life_path).exists():
        raise FileNotFoundError(f"생활 파일을 찾을 수 없음: {life_path}")
    life = read_csv_safely(life_path)

    # 길이 맞추기
    if len(life) != len(env):
        min_len = min(len(life), len(env))
        env = env.iloc[:min_len].reset_index(drop=True)
        life = life.iloc[:min_len].reset_index(drop=True)

    # 날짜 붙이기
    life = life.copy()
    life.insert(0, "date", env["date"].values)

    # 병합
    env_cols = ["date"] + [c for c in env.columns if c != "date"]
    merged = pd.merge(life, env[env_cols], on="date", how="left")

    # 날짜를 YYYYMMDD 정수로 변환
    merged["date"] = merged["date"].dt.strftime("%Y%m%d").astype(int)

    # 저장
    merged.to_csv(out_path, index=False)
    print(f"[INFO] merged saved to {out_path}, shape={merged.shape}")
    return merged

if __name__ == "__main__":
    merge_env_and_life()
