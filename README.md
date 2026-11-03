# Smart Retail Intelligence & Customer Behavior Analytics System

An end-to-end Data Mining and Data Warehousing project that analyzes retail transactions, customer purchasing behavior, product performance, and sales trends.

## Project Overview

The system transforms raw retail transaction data into meaningful business insights using Python, MySQL, data mining techniques, and an interactive Streamlit dashboard.

## Key Features

- Retail transaction data cleaning and preprocessing
- ETL pipeline for MySQL Data Warehouse
- Customer segmentation using RFM analysis and K-Means clustering
- Market Basket Analysis using the Apriori algorithm
- Sales and revenue analytics
- Product and customer performance insights
- Geographic and time-based analysis
- Interactive dashboard with filters and downloadable reports
- Docker-based application deployment
- GitHub Actions CI/CD integration
- Automatic Docker Hub image publishing

## Technology Stack

| Component | Technology |
|---|---|
| Programming | Python |
| Database | MySQL |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Data Mining | Apriori Algorithm |
| Visualization | Plotly, Streamlit |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Image Registry | Docker Hub |

## Dataset

Source: UCI Online Retail Dataset

- Original records: 541,909
- Original columns: 8
- Format: Excel (.xlsx)

The dataset contains retail transaction information such as invoice numbers, product descriptions, quantities, prices, customer IDs, and countries.

## Data Warehouse

The MySQL database uses a dimensional data warehouse structure.

**Dimension Tables**
- dim_customer
- dim_product
- dim_date
- dim_country

**Fact Table**
- fact_sales

## Data Mining Techniques

### 1. RFM Analysis
Analyzes customer behavior using:
- Recency
- Frequency
- Monetary Value

### 2. Customer Segmentation
Uses K-Means clustering to group customers based on purchasing behavior.

### 3. Market Basket Analysis
Uses the Apriori algorithm to discover frequently purchased product combinations and association rules.

## Project Architecture

Raw Dataset → Data Cleaning → ETL Pipeline → MySQL Data Warehouse → Data Mining → Streamlit Dashboard

## Installation

Clone the repository:

```bash
git clone https://github.com/abhishek17011/Smart-Retail-Intelligence.git
cd Smart-Retail-Intelligence
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your database credentials using the project's environment configuration. Never commit passwords or access tokens.

## Run the Dashboard

```bash
streamlit run dashboard/app.py
```

## Docker Deployment

Pull the published image:

```bash
docker pull abhishekzade17/smart-retail-intelligence:latest
```

For database-connected deployment, configure the required MySQL environment variables and database network access before starting the container.

## CI/CD

GitHub Actions automatically builds the Docker image and publishes it to Docker Hub when code is pushed to the main branch.

Docker Hub:

https://hub.docker.com/r/abhishekzade17/smart-retail-intelligence

## Project Structure

```text
Smart-Retail-Intelligence/
├── data/
│   ├── raw/
│   └── processed/
├── database/
│   └── schema.sql
├── src/
├── dashboard/
│   └── app.py
├── tests/
├── .github/
│   └── workflows/
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## Future Enhancements

- Advanced sales forecasting
- Real-time retail analytics
- Product recommendation engine
- Advanced customer lifetime value analysis
- Cloud-based deployment

## Author

**Abhishek Zade**

GitHub: https://github.com/abhishek17011

## License

This project is developed for academic and educational purposes.
