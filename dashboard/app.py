
import os
import io
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 1. CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Retail Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

SALES_FILE = os.path.join(DATA_DIR, "cleaned_retail.csv")
SEGMENT_FILE = os.path.join(DATA_DIR, "customer_segments.csv")
RFM_FILE = os.path.join(DATA_DIR, "rfm_analysis.csv")
RULES_FILE = os.path.join(DATA_DIR, "association_rules.csv")

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101C35, #1B3154);
    }

    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 17px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    }

    [data-testid="stMetricLabel"] {
        color: #64748B;
    }

    [data-testid="stMetricValue"] {
        color: #172554;
        font-weight: 700;
    }

    h1, h2, h3 {
        color: #172554;
    }

    .section-caption {
        color: #64748B;
        font-size: 14px;
    }

    div[data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #E2E8F0;
    }

    .status-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 2. DATA LOADING
# =========================================================

@st.cache_data(show_spinner="Loading retail analytics data...")
def load_data():

    if not os.path.exists(SALES_FILE):
        raise FileNotFoundError(
            "cleaned_retail.csv not found. Run data_cleaning.py."
        )

    sales = pd.read_csv(
        SALES_FILE,
        parse_dates=["InvoiceDate"]
    )

    segments = (
        pd.read_csv(SEGMENT_FILE)
        if os.path.exists(SEGMENT_FILE)
        else pd.DataFrame()
    )

    rfm = (
        pd.read_csv(RFM_FILE)
        if os.path.exists(RFM_FILE)
        else pd.DataFrame()
    )

    rules = (
        pd.read_csv(RULES_FILE)
        if os.path.exists(RULES_FILE)
        else pd.DataFrame()
    )

    sales["TotalAmount"] = pd.to_numeric(
        sales["TotalAmount"], errors="coerce"
    )
    sales["Quantity"] = pd.to_numeric(
        sales["Quantity"], errors="coerce"
    )
    sales["UnitPrice"] = pd.to_numeric(
        sales["UnitPrice"], errors="coerce"
    )

    sales = sales.dropna(
        subset=["InvoiceDate", "TotalAmount", "Quantity"]
    )

    sales["Country"] = sales["Country"].fillna("Unknown")
    sales["Description"] = sales["Description"].fillna("Unknown Product")

    return sales, segments, rfm, rules


# =========================================================
# 3. DATABASE MONITORING
# =========================================================

def get_database_status():

    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "smart_retail_dw"),
        "connection_timeout": 5
    }

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        tables = [
            "dim_customer",
            "dim_product",
            "dim_date",
            "dim_country",
            "fact_sales"
        ]

        counts = {}

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return True, counts, "Database connected successfully"

    except Exception as error:
        return False, {}, str(error)


# =========================================================
# 4. EXPORT FUNCTIONS
# =========================================================

def csv_download(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def excel_download(dataframes):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, frame in dataframes.items():
            if not frame.empty:
                frame.to_excel(
                    writer,
                    sheet_name=name[:31],
                    index=False
                )

    return output.getvalue()


def download_controls(df, filename, label="Download CSV"):

    st.download_button(
        label=label,
        data=csv_download(df),
        file_name=filename,
        mime="text/csv"
    )


# =========================================================
# 5. LOAD APPLICATION DATA
# =========================================================

try:
    sales, segments, rfm, rules = load_data()

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.info("Check data/processed/ and run the required Python scripts.")
    st.stop()


# =========================================================
# 6. SIDEBAR AND GLOBAL FILTERS
# =========================================================

st.sidebar.markdown("# 🛍️ Smart Retail")
st.sidebar.caption("INTELLIGENCE & ANALYTICS")
st.sidebar.divider()

pages = [
    "Executive Overview",
    "Sales Performance",
    "Customer Intelligence",
    "Product Intelligence",
    "Market Basket Analysis",
    "Geographic Analytics",
    "Time Intelligence",
    "Data Warehouse & ETL"
]

page = st.sidebar.radio(
    "NAVIGATION",
    pages
)

st.sidebar.divider()
st.sidebar.markdown("### GLOBAL FILTERS")

min_date = sales["InvoiceDate"].min().date()
max_date = sales["InvoiceDate"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

countries = sorted(sales["Country"].dropna().unique().tolist())

selected_countries = st.sidebar.multiselect(
    "Select countries",
    countries,
    default=countries
)

search_product = st.sidebar.text_input(
    "Search product",
    placeholder="Enter product name..."
)

filtered = sales.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date, end_date = date_range

    filtered = filtered[
        filtered["InvoiceDate"].dt.date.between(
            start_date, end_date
        )
    ]

filtered = filtered[
    filtered["Country"].isin(selected_countries)
]

if search_product:
    filtered = filtered[
        filtered["Description"].str.contains(
            search_product,
            case=False,
            na=False
        )
    ]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

st.sidebar.divider()
st.sidebar.caption("Smart Retail Intelligence | Academic Project")


# =========================================================
# 7. COMMON METRICS
# =========================================================

revenue = filtered["TotalAmount"].sum()
orders = filtered["InvoiceNo"].nunique()
customers = filtered["CustomerID"].nunique()
products = filtered["StockCode"].nunique()
units = filtered["Quantity"].sum()
aov = revenue / orders if orders else 0

def show_header(title, subtitle):
    st.title(title)
    st.markdown(
        f'<p class="section-caption">{subtitle}</p>',
        unsafe_allow_html=True
    )

def show_kpis():

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Revenue", f"£{revenue:,.2f}")
    c2.metric("Total Orders", f"{orders:,}")
    c3.metric("Customers", f"{customers:,}")
    c4.metric("Products", f"{products:,}")
    c5.metric("Average Order Value", f"£{aov:,.2f}")

def revenue_by_month(data):

    temp = data.copy()

    temp["Month"] = (
        temp["InvoiceDate"].dt.to_period("M").astype(str)
    )

    return (
        temp.groupby("Month", as_index=False)["TotalAmount"]
        .sum()
    )

def make_chart(fig, height=400):

    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            color="#334155"
        ),
        margin=dict(l=25, r=25, t=55, b=30),
        hoverlabel=dict(bgcolor="white")
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme="streamlit"
    )


# =========================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =========================================================

if page == "Executive Overview":

    show_header(
        "Executive Overview",
        "Complete retail business performance at a glance."
    )

    show_kpis()

    st.divider()

    monthly = revenue_by_month(filtered)

    left, right = st.columns([1.6, 1])

    with left:

        fig = px.area(
            monthly,
            x="Month",
            y="TotalAmount",
            markers=True,
            title="Revenue Growth Over Time"
        )

        make_chart(fig)

    with right:

        country_data = (
            filtered.groupby("Country")["TotalAmount"]
            .sum()
            .nlargest(8)
            .reset_index()
        )

        fig = px.pie(
            country_data,
            names="Country",
            values="TotalAmount",
            hole=0.55,
            title="Revenue by Country"
        )

        make_chart(fig)

    col1, col2 = st.columns(2)

    top = (
        filtered.groupby("Description")["TotalAmount"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig = px.bar(
        top,
        x="TotalAmount",
        y="Description",
        orientation="h",
        title="Top 10 Revenue Generating Products"
    )

    col1.plotly_chart(fig, use_container_width=True)

    daily = (
        filtered.assign(
            Day=filtered["InvoiceDate"].dt.day_name()
        )
        .groupby("Day")["TotalAmount"]
        .sum()
        .reindex([
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ])
        .reset_index()
    )

    fig = px.bar(
        daily,
        x="Day",
        y="TotalAmount",
        title="Revenue by Weekday"
    )

    col2.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Transactions")

    recent = filtered.sort_values(
        "InvoiceDate", ascending=False
    ).head(100)

    st.dataframe(recent, use_container_width=True)

    download_controls(recent, "recent_transactions.csv")


# =========================================================
# PAGE 2: SALES PERFORMANCE
# =========================================================

elif page == "Sales Performance":

    show_header(
        "Sales Performance Analytics",
        "Explore sales trends, order values and revenue patterns."
    )

    show_kpis()

    st.divider()

    monthly = revenue_by_month(filtered)

    fig = px.line(
        monthly,
        x="Month",
        y="TotalAmount",
        markers=True,
        title="Monthly Sales Trend"
    )

    make_chart(fig, 450)

    col1, col2 = st.columns(2)

    quarterly = filtered.copy()
    quarterly["Quarter"] = (
        quarterly["InvoiceDate"].dt.to_period("Q").astype(str)
    )

    qdata = (
        quarterly.groupby("Quarter")["TotalAmount"]
        .sum().reset_index()
    )

    fig = px.bar(
        qdata,
        x="Quarter",
        y="TotalAmount",
        title="Quarterly Revenue"
    )

    col1.plotly_chart(fig, use_container_width=True)

    order_data = (
        filtered.groupby("InvoiceNo")["TotalAmount"]
        .sum().reset_index()
    )

    fig = px.histogram(
        order_data,
        x="TotalAmount",
        nbins=40,
        title="Order Value Distribution"
    )

    col2.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales Data")
    st.dataframe(monthly, use_container_width=True)

    download_controls(monthly, "monthly_sales.csv")


# =========================================================
# PAGE 3: CUSTOMER INTELLIGENCE
# =========================================================

elif page == "Customer Intelligence":

    show_header(
        "Customer Intelligence",
        "RFM analysis and machine learning based customer segmentation."
    )

    if segments.empty:

        st.warning("Run customer_segmentation.py first.")

    else:

        customer_segments = segments.copy()

        # Restrict customer segmentation to the filtered
        # customer population for geographic/date filters.
        valid_customers = set(filtered["CustomerID"].dropna())

        if "customer_key" in customer_segments.columns:

            conn_ok, counts, message = get_database_status()

            if conn_ok:

                try:
                    conn = mysql.connector.connect(
                        host=os.getenv("DB_HOST", "localhost"),
                        port=int(os.getenv("DB_PORT", "3306")),
                        user=os.getenv("DB_USER", "root"),
                        password=os.getenv("DB_PASSWORD", ""),
                        database=os.getenv("DB_NAME", "smart_retail_dw")
                    )

                    mapping = pd.read_sql(
                        "SELECT customer_key, customer_id FROM dim_customer",
                        conn
                    )

                    conn.close()

                    customer_segments = customer_segments.merge(
                        mapping,
                        on="customer_key",
                        how="left"
                    )

                    customer_segments = customer_segments[
                        customer_segments["customer_id"].isin(
                            valid_customers
                        )
                    ]

                except Exception:
                    pass

        if customer_segments.empty:
            st.info("No customer segmentation records match the current filters.")
        else:

            a, b, c = st.columns(3)

            a.metric("Customers in Analysis", len(customer_segments))
            b.metric(
                "Clusters",
                customer_segments["Cluster"].nunique()
            )
            c.metric(
                "Average Spending",
                f"£{customer_segments['Monetary'].mean():,.2f}"
            )

            st.divider()

            summary = (
                customer_segments.groupby("Cluster")
                [["Recency", "Frequency", "Monetary"]]
                .mean().round(2).reset_index()
            )

            col1, col2 = st.columns(2)

            fig = px.scatter(
                customer_segments,
                x="Frequency",
                y="Monetary",
                color=customer_segments["Cluster"].astype(str),
                hover_data=["Recency"],
                title="K-Means Customer Segments"
            )

            col1.plotly_chart(fig, use_container_width=True)

            fig = px.bar(
                summary,
                x="Cluster",
                y="Monetary",
                color="Cluster",
                title="Average Spending by Cluster"
            )

            col2.plotly_chart(fig, use_container_width=True)

            fig = px.box(
                customer_segments,
                x="Cluster",
                y="Recency",
                color=customer_segments["Cluster"].astype(str),
                title="Customer Recency Distribution"
            )

            make_chart(fig)

            st.subheader("RFM Cluster Summary")
            st.dataframe(summary, use_container_width=True)

            st.subheader("Customer Details")
            st.dataframe(customer_segments, use_container_width=True)

            download_controls(
                customer_segments,
                "customer_segments.csv"
            )

    if not rfm.empty:
        with st.expander("View RFM analysis records"):
            st.dataframe(rfm, use_container_width=True)
            download_controls(rfm, "rfm_analysis.csv")


# =========================================================
# PAGE 4: PRODUCT INTELLIGENCE
# =========================================================

elif page == "Product Intelligence":

    show_header(
        "Product Intelligence",
        "Understand product demand, sales contribution and performance."
    )

    product_data = (
        filtered.groupby(["StockCode", "Description"])
        .agg(
            Revenue=("TotalAmount", "sum"),
            Quantity=("Quantity", "sum"),
            Orders=("InvoiceNo", "nunique")
        )
        .reset_index()
    )

    product_data = product_data.sort_values(
        "Revenue", ascending=False
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Products", len(product_data))
    c2.metric("Units Sold", f"{product_data['Quantity'].sum():,.0f}")
    c3.metric("Product Revenue", f"£{product_data['Revenue'].sum():,.2f}")

    st.divider()

    col1, col2 = st.columns(2)

    fig = px.bar(
        product_data.head(15),
        x="Revenue",
        y="Description",
        orientation="h",
        title="Top 15 Products by Revenue"
    )

    col1.plotly_chart(fig, use_container_width=True)

    fig = px.treemap(
        product_data.head(40),
        path=["Description"],
        values="Revenue",
        title="Product Revenue Treemap"
    )

    col2.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        product_data,
        x="Quantity",
        y="Revenue",
        size="Orders",
        hover_name="Description",
        title="Product Quantity vs Revenue"
    )

    make_chart(fig)

    st.subheader("Product Ranking")

    product_data["Revenue Rank"] = (
        product_data["Revenue"].rank(
            method="dense", ascending=False
        ).astype(int)
    )

    st.dataframe(product_data, use_container_width=True)

    download_controls(product_data, "product_analysis.csv")


# =========================================================
# PAGE 5: MARKET BASKET ANALYSIS
# =========================================================

elif page == "Market Basket Analysis":

    show_header(
        "Market Basket Analysis",
        "Discover frequently purchased product combinations using Apriori."
    )

    if rules.empty:

        st.warning("Run market_basket.py first.")

    else:

        rule_data = rules.copy()

        required = [
            "antecedents", "consequents",
            "support", "confidence", "lift"
        ]

        if all(col in rule_data.columns for col in required):

            rule_data = rule_data.dropna(
                subset=required
            )

            a, b, c = st.columns(3)

            a.metric("Association Rules", len(rule_data))
            b.metric(
                "Average Confidence",
                f"{rule_data['confidence'].mean()*100:.2f}%"
            )
            c.metric(
                "Average Lift",
                f"{rule_data['lift'].mean():.2f}"
            )

            st.divider()

            col1, col2 = st.columns(2)

            fig = px.scatter(
                rule_data,
                x="support",
                y="confidence",
                size="lift",
                color="lift",
                hover_data=["antecedents", "consequents"],
                title="Support vs Confidence"
            )

            col1.plotly_chart(fig, use_container_width=True)

            top_rules = rule_data.nlargest(15, "lift").copy()

            top_rules["Rule"] = (
                top_rules["antecedents"]
                + " → "
                + top_rules["consequents"]
            )

            fig = px.bar(
                top_rules,
                x="lift",
                y="Rule",
                orientation="h",
                title="Top 15 Rules by Lift"
            )

            col2.plotly_chart(fig, use_container_width=True)

            st.subheader("Association Rules Table")

            st.dataframe(
                rule_data[required].sort_values(
                    "confidence", ascending=False
                ),
                use_container_width=True
            )

            download_controls(
                rule_data[required],
                "association_rules.csv"
            )

            st.caption(
                "Support measures transaction coverage, confidence "
                "measures conditional association, and lift compares "
                "observed association against independence."
            )

        else:
            st.error("Association rules file has an unexpected format.")


# =========================================================
# PAGE 6: GEOGRAPHIC ANALYTICS
# =========================================================

elif page == "Geographic Analytics":

    show_header(
        "Geographic Analytics",
        "Analyse customer transactions and revenue across countries."
    )

    geo = (
        filtered.groupby("Country")
        .agg(
            Revenue=("TotalAmount", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique")
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Countries", len(geo))
    c2.metric("Geographic Revenue", f"£{geo['Revenue'].sum():,.2f}")
    c3.metric("Orders", f"{geo['Orders'].sum():,}")

    col1, col2 = st.columns(2)

    fig = px.bar(
        geo.head(15),
        x="Country",
        y="Revenue",
        title="Top 15 Countries by Revenue"
    )

    col1.plotly_chart(fig, use_container_width=True)

    fig = px.choropleth(
        geo,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        hover_data=["Orders", "Customers"],
        color_continuous_scale="Blues",
        title="Global Retail Revenue Map"
    )

    col2.plotly_chart(fig, use_container_width=True)

    st.subheader("Country Performance")
    st.dataframe(geo, use_container_width=True)

    download_controls(geo, "country_analytics.csv")


# =========================================================
# PAGE 7: TIME INTELLIGENCE
# =========================================================

elif page == "Time Intelligence":

    show_header(
        "Time Intelligence",
        "Discover daily, weekly and hourly purchasing patterns."
    )

    time_data = filtered.copy()

    time_data["Weekday"] = (
        time_data["InvoiceDate"].dt.day_name()
    )

    time_data["Hour"] = (
        time_data["InvoiceDate"].dt.hour
    )

    time_data["Day"] = (
        time_data["InvoiceDate"].dt.date
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Active Shopping Days", time_data["Day"].nunique())
    c2.metric("Peak Hour", f"{time_data.groupby('Hour')['TotalAmount'].sum().idxmax()}:00")
    c3.metric("Peak Weekday", time_data.groupby("Weekday")["TotalAmount"].sum().idxmax())

    st.divider()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    heatmap_data = (
        time_data.pivot_table(
            index="Weekday",
            columns="Hour",
            values="TotalAmount",
            aggfunc="sum",
            fill_value=0
        )
        .reindex(weekday_order)
    )

    fig = px.imshow(
        heatmap_data,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Shopping Activity Heatmap: Weekday vs Hour",
        labels=dict(
            x="Hour of Day",
            y="Weekday",
            color="Revenue"
        )
    )

    make_chart(fig, 450)

    col1, col2 = st.columns(2)

    daily = (
        time_data.groupby("Day")["TotalAmount"]
        .sum().reset_index()
    )

    fig = px.line(
        daily,
        x="Day",
        y="TotalAmount",
        title="Daily Revenue Trend"
    )

    col1.plotly_chart(fig, use_container_width=True)

    hourly = (
        time_data.groupby("Hour")["TotalAmount"]
        .sum().reset_index()
    )

    fig = px.bar(
        hourly,
        x="Hour",
        y="TotalAmount",
        title="Hourly Revenue Distribution"
    )

    col2.plotly_chart(fig, use_container_width=True)

    download_controls(heatmap_data.reset_index(), "time_heatmap.csv")


# =========================================================
# PAGE 8: DATA WAREHOUSE & ETL MONITORING
# =========================================================

elif page == "Data Warehouse & ETL":

    show_header(
        "Data Warehouse & ETL Monitoring",
        "Monitor database health, warehouse records and data pipeline files."
    )

    db_ok, db_counts, db_message = get_database_status()

    if db_ok:

        st.success(db_message)

        cols = st.columns(5)

        table_names = [
            "dim_customer",
            "dim_product",
            "dim_date",
            "dim_country",
            "fact_sales"
        ]

        for col, table in zip(cols, table_names):

            col.metric(
                table.replace("_", " ").title(),
                f"{db_counts[table]:,}"
            )

    else:

        st.error("MySQL database connection unavailable.")
        st.caption(db_message)

    st.divider()

    st.subheader("Data Pipeline File Monitoring")

    files = {
        "Cleaned Retail Dataset": SALES_FILE,
        "Customer Segmentation": SEGMENT_FILE,
        "RFM Analysis": RFM_FILE,
        "Association Rules": RULES_FILE
    }

    file_records = []

    for name, path in files.items():

        exists = os.path.exists(path)

        file_records.append({
            "Component": name,
            "Status": "Available" if exists else "Missing",
            "Size (MB)": (
                round(os.path.getsize(path) / (1024 * 1024), 2)
                if exists else 0
            ),
            "Last Modified": (
                pd.Timestamp(
                    os.path.getmtime(path), unit="s"
                ).strftime("%Y-%m-%d %H:%M:%S")
                if exists else "Not generated"
            )
        })

    file_df = pd.DataFrame(file_records)

    st.dataframe(file_df, use_container_width=True)

    available = sum(
        os.path.exists(path) for path in files.values()
    )

    st.progress(
        available / len(files),
        text=f"{available}/{len(files)} pipeline output files available"
    )

    st.divider()

    st.subheader("Data Quality Summary")

    quality = pd.DataFrame([
        {
            "Metric": "Total cleaned records",
            "Value": len(sales)
        },
        {
            "Metric": "Missing Customer IDs",
            "Value": int(sales["CustomerID"].isna().sum())
        },
        {
            "Metric": "Duplicate records",
            "Value": int(sales.duplicated().sum())
        },
        {
            "Metric": "Invalid quantities",
            "Value": int((sales["Quantity"] <= 0).sum())
        },
        {
            "Metric": "Invalid unit prices",
            "Value": int((sales["UnitPrice"] <= 0).sum())
        }
    ])

    st.dataframe(quality, use_container_width=True)

    st.subheader("Data Warehouse Architecture")

    architecture = pd.DataFrame({
        "Warehouse Table": [
            "dim_customer",
            "dim_product",
            "dim_date",
            "dim_country",
            "fact_sales"
        ],
        "Purpose": [
            "Customer information",
            "Product information",
            "Calendar information",
            "Geographic information",
            "Sales transaction facts"
        ],
        "Current Records": [
            db_counts.get("dim_customer", 0),
            db_counts.get("dim_product", 0),
            db_counts.get("dim_date", 0),
            db_counts.get("dim_country", 0),
            db_counts.get("fact_sales", 0)
        ] if db_ok else ["Unavailable"] * 5
    })

    st.dataframe(architecture, use_container_width=True)

    if db_ok:
        st.success("MySQL warehouse connection and table checks passed.")

    st.caption(
        "Note: File timestamps represent last modification times, "
        "not necessarily the exact ETL completion time."
    )


# =========================================================
# 9. GLOBAL EXPORT
# =========================================================

st.sidebar.divider()
st.sidebar.markdown("### EXPORT REPORTS")

st.sidebar.download_button(
    "⬇ Download Filtered CSV",
    data=csv_download(filtered),
    file_name="smart_retail_filtered_report.csv",
    mime="text/csv",
    use_container_width=True
)

st.sidebar.download_button(
    "⬇ Download Excel Report",
    data=excel_download({
        "Sales": filtered.head(100000),
        "Customers": segments,
        "RFM": rfm,
        "Association Rules": rules
    }),
    file_name="smart_retail_analytics_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.sidebar.caption(
    "© Smart Retail Intelligence | Python + MySQL + Data Mining + DevOps"
)
