import pandas as pd
from pathlib import Path

#폴더 위치 지정
RAW = Path("data/raw")
OUT = Path("data/processed")

#utf-8 -> cp949
def read_csv_safely(path, names, usecols):
    try:
        return pd.read_csv(path, header=None, names=names, usecols=usecols, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, header=None, names=names, usecols=usecols, encoding="cp949")

#숫자형이면 문자열로, 문자열이면 공백 제거
def normalize_date_col(df, col="date"):
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = pd.to_datetime(df[col].astype(str), format="%Y%m%d", errors="coerce")
    else:
        df[col] = pd.to_datetime(df[col].astype(str).str.strip(), errors="coerce")
    df.dropna(subset=[col], inplace=True)
    return df

#csv 파일의 0,1,2행만 읽고 date행을 날짜 타입으로 저장
def merge_env_data_simple():
    pm = read_csv_safely(RAW / "pm.csv", ["date", "region", "PM10"], [0, 1, 2])
    tp = read_csv_safely(RAW / "temp.csv", ["date", "region", "Temp"], [0, 1, 2])
    hm = read_csv_safely(RAW / "humidity.csv", ["date", "region", "Humidity"], [0, 1, 2])

    pm = normalize_date_col(pm, "date")
    tp = normalize_date_col(tp, "date")
    hm = normalize_date_col(hm, "date")

    #안에 값이 잇으면 merge
    df = (
        pm.merge(tp[["date", "Temp"]], on="date", how="inner")
          .merge(hm[["date", "Humidity"]], on="date", how="inner")
          .sort_values("date")
          .reset_index(drop=True)
    )

    # 엑셀이 텍스트로 인식하도록 날짜 앞에 ' 붙여 저장
    df_out = df.copy()
    df_out["date"] = "'" + df_out["date"].dt.strftime("%Y-%m-%d")
    df_out.to_csv(OUT / "env_merged.csv", index=False, encoding="utf-8-sig")

    print(f"[INFO] Saved: {OUT/'env_merged.csv'}")
    return df

if __name__ == "__main__":
    merge_env_data_simple()
