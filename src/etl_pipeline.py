
import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = "data/processed/cleaned_retail.csv"

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def run_etl():

    print("=" * 55)
    print("SMART RETAIL INTELLIGENCE SYSTEM")
    print("ETL PIPELINE STARTED")
    print("=" * 55)

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            "Cleaned CSV not found. Run data_cleaning.py first."
        )

    # EXTRACT
    print("\n1. Extracting data...")

    df = pd.read_csv(CSV_PATH)

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Quantity"] = df["Quantity"].astype(int)
    df["UnitPrice"] = df["UnitPrice"].astype(float)
    df["TotalAmount"] = df["TotalAmount"].astype(float)

    print("Extracted records:", len(df))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # TRANSFORM + LOAD: CUSTOMER DIMENSION
        print("\n2. Loading customer dimension...")

        customers = df[["CustomerID"]].drop_duplicates()

        cursor.executemany(
            """
            INSERT INTO dim_customer (customer_id)
            VALUES (%s)
            """,
            [(int(x),) for x in customers["CustomerID"]]
        )

        conn.commit()

        # PRODUCT DIMENSION
        print("3. Loading product dimension...")

        products = df[["StockCode", "Description"]].drop_duplicates(
            subset=["StockCode"]
        )

        cursor.executemany(
            """
            INSERT INTO dim_product (stock_code, description)
            VALUES (%s, %s)
            """,
            [
                (str(row.StockCode), str(row.Description))
                for row in products.itertuples(index=False)
            ]
        )

        conn.commit()

        # COUNTRY DIMENSION
        print("4. Loading country dimension...")

        countries = df[["Country"]].drop_duplicates()

        cursor.executemany(
            """
            INSERT INTO dim_country (country_name)
            VALUES (%s)
            """,
            [(str(x),) for x in countries["Country"]]
        )

        conn.commit()

        # DATE DIMENSION
        print("5. Loading date dimension...")

        dates = pd.DataFrame({
            "full_date": df["InvoiceDate"].dt.normalize().unique()
        })

        dates["date_key"] = (
            dates["full_date"].dt.strftime("%Y%m%d").astype(int)
        )
        dates["day"] = dates["full_date"].dt.day
        dates["month"] = dates["full_date"].dt.month
        dates["month_name"] = dates["full_date"].dt.month_name()
        dates["quarter"] = dates["full_date"].dt.quarter
        dates["year"] = dates["full_date"].dt.year

        cursor.executemany(
            """
            INSERT INTO dim_date
            (date_key, full_date, day, month,
             month_name, quarter, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    int(row.date_key),
                    row.full_date.date(),
                    int(row.day),
                    int(row.month),
                    str(row.month_name),
                    int(row.quarter),
                    int(row.year)
                )
                for row in dates.itertuples(index=False)
            ]
        )

        conn.commit()

        # FETCH DIMENSION KEYS
        print("6. Preparing fact table mappings...")

        cursor.execute(
            "SELECT customer_key, customer_id FROM dim_customer"
        )
        customer_map = {b: a for a, b in cursor.fetchall()}

        cursor.execute(
            "SELECT product_key, stock_code FROM dim_product"
        )
        product_map = {b: a for a, b in cursor.fetchall()}

        cursor.execute(
            "SELECT country_key, country_name FROM dim_country"
        )
        country_map = {b: a for a, b in cursor.fetchall()}

        cursor.execute(
            "SELECT date_key, date_key FROM dim_date"
        )
        date_map = {b: a for a, b in cursor.fetchall()}

        # LOAD FACT TABLE IN BATCHES
        print("7. Loading sales fact table...")

        batch_size = 5000
        total_loaded = 0

        insert_sql = """
            INSERT INTO fact_sales
            (invoice_no, customer_key, product_key,
             date_key, country_key, quantity,
             unit_price, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        for start in range(0, len(df), batch_size):

            batch = df.iloc[start:start + batch_size]
            records = []

            for row in batch.itertuples(index=False):

                date_key = int(row.InvoiceDate.strftime("%Y%m%d"))

                records.append((
                    str(row.InvoiceNo),
                    customer_map[int(row.CustomerID)],
                    product_map[str(row.StockCode)],
                    date_map[date_key],
                    country_map[str(row.Country)],
                    int(row.Quantity),
                    float(row.UnitPrice),
                    float(row.TotalAmount)
                ))

            cursor.executemany(insert_sql, records)
            conn.commit()

            total_loaded += len(records)

            print("Loaded records:", total_loaded)

        print("\n" + "=" * 55)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 55)

        print("Customers:", len(customer_map))
        print("Products:", len(product_map))
        print("Countries:", len(country_map))
        print("Fact sales records:", total_loaded)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_etl()
