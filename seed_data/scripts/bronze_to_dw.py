"""
Script: bronze_to_dw.py
Mục đích:
    - Đọc các tệp dữ liệu thô (Bronze Layer) trực tiếp từ MinIO Data Lake.
    - Tạo các schema riêng biệt trong PostgreSQL Data Warehouse:
        + raw_shopee
        + raw_lazada
        + raw_tiktokshop
        + raw_marketing
    - Nạp dữ liệu vào các bảng tương ứng để sẵn sàng cho dbt thực hiện Transform.
"""

import io
import os
import boto3
import pandas as pd
from botocore.client import Config
from sqlalchemy import create_engine, text

# 1. Cấu hình kết nối MinIO
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "REDACTED_MINIO_PASSWORD"
BUCKET_NAME = "lakehouse"

# 2. Cấu hình kết nối PostgreSQL Data Warehouse
DB_USER = "postgres"
DB_PASS = "REDACTED_POSTGRES_PASSWORD"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecom_dw"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("--- BẮT ĐẦU CHUYỂN DỮ LIỆU TỪ BRONZE LAKEHOUSE SANG DATA WAREHOUSE ---")

# 3. Khởi tạo S3 Client và SQLAlchemy Engine
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)

engine = create_engine(DATABASE_URL)

# 4. Danh sách mapping từ MinIO Object sang PostgreSQL Schema & Table
tasks = [
    {
        "s3_key": "bronze/orders/shopee/shopee_orders.csv",
        "schema": "raw_shopee",
        "table": "orders"
    },
    {
        "s3_key": "bronze/orders/lazada/lazada_orders.csv",
        "schema": "raw_lazada",
        "table": "orders"
    },
    {
        "s3_key": "bronze/orders/tiktok/tiktok_orders.csv",
        "schema": "raw_tiktokshop",
        "table": "orders"
    },
    {
        "s3_key": "bronze/marketing/marketing_ad_spend.csv",
        "schema": "raw_marketing",
        "table": "ad_spend"
    }
]

# 5. Thực thi đọc stream từ MinIO và ghi vào PostgreSQL
with engine.connect() as conn:
    for task in tasks:
        s3_key = task["s3_key"]
        schema = task["schema"]
        table = task["table"]

        print(f"\nĐang tải từ MinIO: s3://{BUCKET_NAME}/{s3_key} ...")
        
        # Đọc dữ liệu trực tiếp từ stream của MinIO vào bộ nhớ RAM
        obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        
        print(f"-> Đọc thành công {len(df):,} dòng. Đang nạp vào PostgreSQL: {schema}.{table} ...")

        # Tạo Schema trong Postgres nếu chưa có
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
        conn.commit()

        # Ghi đè (replace) hoặc thêm mới dữ liệu vào bảng
        df.to_sql(
            name=table,
            con=engine,
            schema=schema,
            if_exists="replace",
            index=False,
            chunksize=5000,
            method="multi"
        )
        print(f"-> Đã ghi thành công vào bảng: {schema}.{table}")

print("\n--- HOÀN TẤT ĐỔ DỮ LIỆU VÀO DATA WAREHOUSE THÀNH CÔNG ---")