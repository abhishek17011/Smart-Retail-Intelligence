
import pandas as pd
import os

INPUT_PATH = "data/raw/Online Retail.xlsx"
OUTPUT_PATH = "data/processed/cleaned_retail.csv"

def clean_dataset():

    print("=" * 55)
    print("SMART RETAIL INTELLIGENCE SYSTEM")
    print("DATA CLEANING AND PREPROCESSING")
    print("=" * 55)

    # Load original dataset
    df = pd.read_excel(INPUT_PATH, engine="openpyxl")

    original_rows = len(df)

    print("\nOriginal records:", original_rows)

    # Step 1: Remove duplicate records
    duplicates = df.duplicated().sum()
    df = df.drop_duplicates()

    print("Duplicates removed:", duplicates)

    # Step 2: Remove missing Customer IDs
    missing_customers = df["CustomerID"].isnull().sum()
    df = df.dropna(subset=["CustomerID"])

    print("Missing Customer IDs removed:", missing_customers)

    # Step 3: Convert data types
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )

    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )

    # Step 4: Remove invalid dates
    invalid_dates = df["InvoiceDate"].isnull().sum()
    df = df.dropna(subset=["InvoiceDate"])

    print("Invalid dates removed:", invalid_dates)

    # Step 5: Remove cancelled invoices
    cancelled = df["InvoiceNo"].astype(str).str.startswith("C")
    cancelled_count = cancelled.sum()

    df = df[~cancelled]

    print("Cancelled transactions removed:", cancelled_count)

    # Step 6: Remove invalid quantity
    invalid_quantity = (df["Quantity"] <= 0).sum()
    df = df[df["Quantity"] > 0]

    print("Invalid quantities removed:", invalid_quantity)

    # Step 7: Remove invalid prices
    invalid_prices = (df["UnitPrice"] <= 0).sum()
    df = df[df["UnitPrice"] > 0]

    print("Invalid prices removed:", invalid_prices)

    # Step 8: Handle missing descriptions
    df["Description"] = df["Description"].fillna(
        "Unknown Product"
    )

    # Step 9: Calculate total revenue
    df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]

    # Step 10: Standardize customer IDs
    df["CustomerID"] = df["CustomerID"].astype(int)

    # Save cleaned dataset
    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nFinal records:", len(df))
    print("Records removed:", original_rows - len(df))

    print("\nTotal Revenue:")
    print(round(df["TotalAmount"].sum(), 2))

    print("\nUnique Customers:")
    print(df["CustomerID"].nunique())

    print("\nUnique Products:")
    print(df["StockCode"].nunique())

    print("\nCleaned dataset saved at:", OUTPUT_PATH)

    print("\n" + "=" * 55)
    print("DATA CLEANING COMPLETED SUCCESSFULLY")
    print("=" * 55)


if __name__ == "__main__":
    clean_dataset()
