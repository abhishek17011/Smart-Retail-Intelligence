
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw/Online Retail.xlsx")

def inspect_dataset():
    print("=" * 50)
    print("SMART RETAIL INTELLIGENCE SYSTEM")
    print("DATASET INSPECTION")
    print("=" * 50)

    if not DATA_PATH.exists():
        print("ERROR: Dataset not found!")
        return

    print("\nLoading dataset...")
    df = pd.read_excel(DATA_PATH, engine="openpyxl")

    print("\nDataset loaded successfully!")

    print("\nDataset Shape:")
    print(df.shape)

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Records:")
    print(df.duplicated().sum())

    print("\nUnique Customers:")
    print(df["CustomerID"].nunique())

    print("\nUnique Products:")
    print(df["StockCode"].nunique())

    print("\nDATASET INSPECTION COMPLETED")

if __name__ == "__main__":
    inspect_dataset()
