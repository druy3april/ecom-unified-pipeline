# E-Commerce Unified Analytics Pipeline

Pipeline local end-to-end hợp nhất dữ liệu đơn hàng đa kênh (Shopee, Lazada, TikTok Shop) và chi phí quảng cáo vào PostgreSQL. MinIO đóng vai trò Bronze data lake, dbt tạo các lớp staging/intermediate/marts và file Power BI cung cấp lớp báo cáo.

## Kiến trúc

```text
CSV input -> Python -> MinIO Bronze -> PostgreSQL raw_* -> dbt -> marts -> Power BI
```

Các model dbt hiện có gồm 4 staging models, 1 intermediate model và 3 mart models: `dim_channels`, `fact_orders_daily` và `fact_marketing_daily`.

## Yêu cầu

- Docker và Docker Compose
- Python 3.10+
- Power BI Desktop (chỉ cần nếu mở báo cáo)

## Chạy local

1. Tạo cấu hình local và khởi động dịch vụ:

   ```bash
   cp .env.example .env
   # Đổi các password trong .env trước khi dùng ở môi trường chia sẻ.
   docker compose up -d
   ```

   MinIO Console: <http://localhost:9001>
   PostgreSQL: `localhost:5432`, database `ecom_dw`

2. Cài dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   set -a; source .env; set +a
   ```

3. Chuẩn bị dữ liệu Olist trong `seed_data/raw/`. Các file đầu vào cần có:
   `olist_orders_dataset.csv`, `olist_order_payments_dataset.csv`, cùng các file Olist còn lại nếu cần phân tích mở rộng. Dataset và các file CSV sinh ra không được commit vào repository.

4. Tạo dữ liệu theo kênh, sinh ad spend, upload Bronze và nạp PostgreSQL:

   ```bash
   python seed_data/scripts/split_olist_channels.py
   python seed_data/scripts/generate_marketing_data.py
   python seed_data/scripts/upload_to_datalake.py
   python seed_data/scripts/bronze_to_dw.py
   ```

5. Chạy dbt:

   ```bash
   cd dbt_ecom
   dbt build --profiles-dir .
   ```

## Cấu trúc chính

```text
dbt_ecom/                  # dbt project, models và tests
seed_data/scripts/         # Tạo, upload và nạp dữ liệu
seed_data/raw/             # Dataset local, không commit
seed_data/processed/       # CSV trung gian, không commit
powerbi/                   # Báo cáo Power BI
docker-compose.yml         # PostgreSQL + MinIO
```

## Mô hình dữ liệu

- `dim_channels`: danh mục kênh bán hàng và marketing.
- `fact_orders_daily`: GMV, net revenue và trạng thái đơn theo ngày/kênh.
- `fact_marketing_daily`: ad spend, impressions, clicks, CPC và CTR theo ngày/campaign.

## Ghi chú bảo mật và GitHub

- Không commit `.env`, credentials, `dbt_ecom/target/`, logs hoặc dữ liệu CSV.
- `.env.example` chỉ chứa giá trị mẫu cho local development.
- File PBIX là artifact tùy chọn; cần kiểm tra lại connection/data source trong Power BI Desktop trước khi chia sẻ công khai.
