import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

def relabel(df: pd.DataFrame) -> pd.DataFrame:
    """MoodScore 기반으로 1~5등급 라벨링"""
    # 분위수 기준으로 균등하게 나눔
    df["ConditionLabel"] = pd.qcut(
        df["MoodScore"],
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    return df

def main():
    # synth_merge 결과 불러오기
    df = pd.read_csv(OUT / "life_synth_merged.csv")

    # 라벨링
    df = relabel(df)

    # train/val/test 분리
    train, temp = train_test_split(df, test_size=0.2, random_state=42, stratify=df["ConditionLabel"])
    val, test = train_test_split(temp, test_size=0.5, random_state=42, stratify=temp["ConditionLabel"])

    # 저장
    train.to_csv(OUT / "train.csv", index=False)
    val.to_csv(OUT / "val.csv", index=False)
    test.to_csv(OUT / "test.csv", index=False)

    print(f"[INFO] saved train/val/test")
    print(f"train={train.shape}, val={val.shape}, test={test.shape}")
    print(f"label distribution:\n{df['ConditionLabel'].value_counts(normalize=True)}")

if __name__ == "__main__":
    main()
