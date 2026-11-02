CREATE DATABASE smart_retail_dw;

USE smart_retail_dw;


USE smart_retail_dw;

-- 1. Customer Dimension
CREATE TABLE dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL UNIQUE
);

-- 2. Product Dimension
CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(500)
);

-- 3. Date Dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT,
    year INT
);

-- 4. Country Dimension
CREATE TABLE dim_country (
    country_key INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

-- 5. Sales Fact Table
CREATE TABLE fact_sales (
    sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(30) NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    date_key INT NOT NULL,
    country_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    total_amount DECIMAL(14,2) NOT NULL,

    FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    FOREIGN KEY (country_key)
        REFERENCES dim_country(country_key)
);

-- Verify all tables
SHOW TABLES;
