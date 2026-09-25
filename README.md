# 🛒 End-to-End E-Commerce Multi-Channel Analytics Pipeline

Một kiến trúc Data Pipeline hoàn chỉnh thu thập, chuẩn hóa dữ liệu giao dịch đa sàn TMĐT (Shopee, Lazada, TikTok Shop) và dữ liệu chi phí quảng cáo (Meta, Google, TikTok Ads), biến đổi theo mô hình Star Schema bằng **dbt Core** và trực quan hóa hiệu quả kinh doanh, chỉ số hoàn vốn quảng cáo (**Blended ROAS**) trên **Power BI**.

---

## 🏗️ Kiến trúc hệ thống (System Architecture)
[CSV Sources: Shopee / Lazada / TikTok Shop / Ad Spend]
│
▼ (Python Ingestion)
[MinIO Object Storage (Bronze Lakehouse)]
│
▼ (Streaming Batch Ingestion)
[PostgreSQL DW (Raw Staging Schemas)]
│
▼ (dbt Core Transformation)
├── Staging Layer (stg_*)
├── Intermediate Layer (int_orders_unified)
└── Marts Layer (dim_dates, dim_channels, fact_orders_daily, fact_marketing_daily)
│
▼ (Import Connection)
[Power BI Desktop (Star Schema Serving)]
├── Executive Sales Overview Dashboard
└── Marketing & ROAS Performance Dashboard

---

## 🛠️ Công nghệ sử dụng (Tech Stack)

* **Infrastructure & Containerization:** Docker, Docker Compose
* **Data Lakehouse (Storage):** MinIO (S3-compatible Object Storage)
* **Data Warehouse:** PostgreSQL
* **Data Transformation & Modeling:** dbt Core (Postgres Adapter), SQL
* **Data Ingestion:** Python (`boto3`, `pandas`, `psycopg2`, `sqlalchemy`)
* **Serving Layer & Business Intelligence:** Power BI Desktop, DAX

---

## 📂 Cấu trúc thư mục (Repository Structure)

```text
ecom-unified-pipeline/
├── dbt_ecom/                      # Dự án dbt Core
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/               # Làm sạch, ép kiểu schema từng sàn
│       ├── intermediate/          # Hợp nhất đa sàn TMĐT (int_orders_unified)
│       └── marts/                 # Bảng Fact & Dimension phục vụ BI
├── docker-compose.yml             # Khởi tạo MinIO & PostgreSQL container
├── powerbi/
│   └── Ecom_Unified_Analytics.pbix # Dashboard hoàn thiện
├── seed_data/                     # Scripts tạo mock data và nạp dữ liệu
│   └── scripts/
│       ├── generate_mock_data.py  # Tạo dữ liệu giả lập 100k+ đơn hàng
│       ├── local_to_bronze.py     # Nạp file local lên MinIO Bronze
│       └── bronze_to_dw.py        # Đổ dữ liệu từ MinIO vào PostgreSQL Raw
└── README.md

🚀 Hướng dẫn triển khai dự án (Getting Started)
1. Khởi động hạ tầng Docker
Bash
docker compose up -d
MinIO Console: http://localhost:9001 (User: minioadmin / Pass: minioadmin123)

PostgreSQL DW: localhost:5432 (User: postgres / Database: ecom_dw)

2. Thiết lập môi trường và nạp dữ liệu
Bash
# Tạo môi trường ảo và cài đặt thư viện
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install dbt-postgres

# Sinh dữ liệu và nạp qua Bronze Lakehouse vào Data Warehouse
python seed_data/scripts/generate_mock_data.py
python seed_data/scripts/local_to_bronze.py
python seed_data/scripts/bronze_to_dw.py

3. Thực thi biến đổi và kiểm định chất lượng với dbt
Bash
cd dbt_ecom
dbt build --profiles-dir .

(Toàn bộ 8 models và 11 tests kiểm tra tính duy nhất, khóa ngoại và ràng buộc not-null đều đạt 100%).

📊 Mô hình dữ liệu & Báo cáo Power BI (Data Marts & BI)
Mô hình Star Schema:
dim_channels: Kênh phân phối và loại hình tiếp thị.

Dim_Date: Bảng chiều lịch tự động phục vụ Time-Intelligence.

fact_orders_daily: Tổng hợp doanh thu gộp (GMV), doanh thu thuần (Net Revenue), tỷ lệ hủy đơn theo ngày.

fact_marketing_daily: Chi phí quảng cáo, lượt hiển thị, click, CPC và CTR theo chiến dịch.

Các chỉ số DAX cốt lõi:
Total Net Revenue: Doanh thu thực tế sau khi loại bỏ các đơn hủy.

Average Order Value (AOV): Doanh thu trung bình trên mỗi đơn hoàn tất.

Cancellation Rate: Tỷ lệ hủy đơn hàng đa sàn.

Real Blended ROAS: Tỷ suất hoàn vốn quảng cáo thực tế tính trên doanh thu thuần đã đối soát.