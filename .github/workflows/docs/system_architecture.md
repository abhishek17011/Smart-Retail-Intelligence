
flowchart TD
    A["UCI Online Retail Dataset<br/>541,909 Records"] --> B["Data Inspection"]
    B --> C["Data Cleaning & Preprocessing"]
    C --> D["Processed Retail CSV"]

    D --> E["ETL Pipeline"]
    E --> F[("MySQL Data Warehouse")]

    F --> G["dim_customer"]
    F --> H["dim_product"]
    F --> I["dim_date"]
    F --> J["dim_country"]
    F --> K["fact_sales"]

    F --> L["Data Mining & Analytics"]

    L --> M["RFM Analysis"]
    L --> N["K-Means Customer Segmentation"]
    L --> O["Apriori Market Basket Analysis"]

    M --> P["Streamlit Dashboard"]
    N --> P
    O --> P

    P --> Q["Sales & Revenue Insights"]
    P --> R["Customer & Product Analytics"]
    P --> S["Interactive Charts & Reports"]

    T["GitHub Repository"] --> U["GitHub Actions CI/CD"]
    U --> V["Docker Build"]
    V --> W[("Docker Hub")]
    W --> X["Docker Container Deployment"]
    X --> P
