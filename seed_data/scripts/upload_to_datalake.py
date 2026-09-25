"""
Script: upload_to_datalake.py
Mục đích:
    - Kết nối với MinIO Object Storage qua S3 API bằng boto3.
    - Khởi tạo bucket 'lakehouse' (nếu chưa tồn tại).
    - Tải toàn bộ 4 file CSV trong seed_data/processed/ lên Data Lake
      theo cấu trúc phân cấp Bronze Layer chuẩn công nghiệp:
        bronze/orders/<platform>/...
        bronze/marketing/...
"""

import os
import boto3
from botocore.client import Config

# 1. Cấu hình thông số kết nối MinIO S3
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "REDACTED_MINIO_PASSWORD"
BUCKET_NAME = "lakehouse"

PROCESSED_DIR = "seed_data/processed"

print("--- BẮT ĐẦU NẠP DỮ LIỆU VÀO MINIO DATA LAKE ---")

# 2. Khởi tạo S3 Client kết nối tới MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)

# 3. Kiểm tra hoặc tạo Bucket 'lakehouse'
try:
    s3_client.head_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' đã tồn tại sẵn trên Data Lake.")
except Exception:
    print(f"Bucket '{BUCKET_NAME}' chưa có. Đang tiến hành tạo mới...")
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    print(f"-> Tạo thành công bucket '{BUCKET_NAME}'.")

# 4. Danh sách các file cần nạp và đường dẫn S3 Key (Bronze Layer)
files_to_upload = [
    {
        "local_path": os.path.join(PROCESSED_DIR, "shopee_orders.csv"),
        "s3_key": "bronze/orders/shopee/shopee_orders.csv"
    },
    {
        "local_path": os.path.join(PROCESSED_DIR, "lazada_orders.csv"),
        "s3_key": "bronze/orders/lazada/lazada_orders.csv"
    },
    {
        "local_path": os.path.join(PROCESSED_DIR, "tiktok_orders.csv"),
        "s3_key": "bronze/orders/tiktok/tiktok_orders.csv"
    },
    {
        "local_path": os.path.join(PROCESSED_DIR, "marketing_ad_spend.csv"),
        "s3_key": "bronze/marketing/marketing_ad_spend.csv"
    }
]

# 5. Thực hiện upload từng file
for item in files_to_upload:
    local_file = item["local_path"]
    s3_key = item["s3_key"]
    
    if os.path.exists(local_file):
        file_size_mb = os.path.getsize(local_file) / (1024 * 1024)
        print(f"Đang nạp: {local_file} ({file_size_mb:.2f} MB) -> s3://{BUCKET_NAME}/{s3_key} ...")
        s3_client.upload_file(local_file, BUCKET_NAME, s3_key)
        print(f"-> Tải lên thành công!")
    else:
        print(f"Cảnh báo: Không tìm thấy file {local_file}!")

print("\n--- HOÀN TẤT NẠP DỮ LIỆU VÀO DATA LAKE ---")