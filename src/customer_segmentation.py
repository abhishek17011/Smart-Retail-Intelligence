
import os
import mysql.connector
import pandas as pd
import numpy as np

from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

load_dotenv()

OUTPUT_DIR = "data/processed"


def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def run_customer_segmentation():

    print("=" * 55)
    print("SMART RETAIL INTELLIGENCE SYSTEM")
    print("CUSTOMER SEGMENTATION USING K-MEANS")
    print("=" * 55)

    conn = get_connection()

    query = """
        SELECT
            f.customer_key,
            COUNT(DISTINCT f.invoice_no) AS Frequency,
            SUM(f.total_amount) AS Monetary,
            DATEDIFF(
                (SELECT MAX(full_date) + INTERVAL 1 DAY
                 FROM dim_date),
                MAX(d.full_date)
            ) AS Recency
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        GROUP BY f.customer_key
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("\nCustomer records:", len(df))

    # Handle invalid values
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    # Prepare RFM data
    rfm = df[["Recency", "Frequency", "Monetary"]].copy()

    # Log transformation
    rfm_log = np.log1p(rfm)

    # Standardize values
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(rfm_log)

    # K-Means clustering
    model = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10
    )

    df["Cluster"] = model.fit_predict(scaled_data)

    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df.to_csv(
        os.path.join(OUTPUT_DIR, "customer_segments.csv"),
        index=False
    )

    rfm.to_csv(
        os.path.join(OUTPUT_DIR, "rfm_analysis.csv"),
        index=False
    )

    print("\nCUSTOMER SEGMENTATION COMPLETED!")

    print("\nCluster Distribution:")
    print(df["Cluster"].value_counts().sort_index())

    print("\nCluster Analysis:")
    print(
        df.groupby("Cluster")[
            ["Recency", "Frequency", "Monetary"]
        ].mean().round(2)
    )

    print("\nFiles saved:")
    print("customer_segments.csv")
    print("rfm_analysis.csv")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    run_customer_segmentation()
