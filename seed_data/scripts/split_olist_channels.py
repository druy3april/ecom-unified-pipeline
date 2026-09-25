"""
Script: split_olist_channels.py
Mục đích:
    - Đọc dữ liệu đơn hàng và thanh toán thật từ Olist.
    - Phân chia tập đơn hàng thành 3 sàn TMĐT theo tỷ lệ thị phần thực tế:
        + Shopee: 45%
        + Lazada: 30%
        + TikTok Shop: 25%
    - Giả lập cấu trúc cột (Schema) khác nhau cho từng sàn để phục vụ
      bài toán chuẩn hóa dữ liệu (Staging Layer) trong dbt sau này.
"""

import os
import pandas as pd
import numpy as np

# 1. Định nghĩa đường dẫn thư mục
RAW_DIR = "seed_data/raw"
PROCESSED_DIR = "seed_data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("--- BẮT ĐẦU XỬ LÝ PHÂN TÁCH KÊNH BÁN HÀNG ---")

# 2. Đọc file đơn hàng và file thanh toán gốc từ Olist
orders_file = os.path.join(RAW_DIR, "olist_orders_dataset.csv")
payments_file = os.path.join(RAW_DIR, "olist_order_payments_dataset.csv")

print(f"Đang đọc dữ liệu từ: {orders_file}")
df_orders = pd.read_csv(orders_file)

print(f"Đang đọc dữ liệu từ: {payments_file}")
df_payments = pd.read_csv(payments_file)

# 3. Tính tổng tiền thanh toán cho mỗi đơn hàng (1 đơn có thể trả bằng nhiều phương thức)
# Gom nhóm theo order_id và tính tổng cột payment_value
df_order_totals = (
    df_payments.groupby("order_id")["payment_value"]
    .sum()
    .reset_index()
    .rename(columns={"payment_value": "total_amount"})
)

# Merge tổng tiền vào bảng đơn hàng chính
df_merged = pd.merge(df_orders, df_order_totals, on="order_id", how="left")
# Xử lý các đơn không có giá trị thanh toán (điền giá trị mặc định 0)
df_merged["total_amount"] = df_merged["total_amount"].fillna(0)

total_records = len(df_merged)
print(f"Tổng số đơn hàng thực tế đọc được: {total_records:,} đơn.")

# 4. Gán nhãn sàn TMĐT ngẫu nhiên theo tỷ trọng thị phần thực tế
# Seed 42 giúp kết quả ngẫu nhiên luôn cố định qua các lần chạy
np.random.seed(42)
channels = np.random.choice(
    ["shopee", "lazada", "tiktokshop"],
    size=total_records,
    p=[0.45, 0.30, 0.25]
)
df_merged["channel"] = channels

# 5. Tách và tạo dữ liệu theo cấu trúc cột riêng của từng sàn

# --- SÀN SHOPEE (Thị phần 45%) ---
print("\nĐang xuất dữ liệu kênh Shopee...")
shopee_raw = df_merged[df_merged["channel"] == "shopee"].copy()
shopee_df = pd.DataFrame({
    "order_sn": "SP_" + shopee_raw["order_id"].astype(str),
    "customer_id": shopee_raw["customer_id"],
    "create_time": shopee_raw["order_purchase_timestamp"],
    "order_status": shopee_raw["order_status"].str.upper(),
    "total_amount": shopee_raw["total_amount"]
})
shopee_path = os.path.join(PROCESSED_DIR, "shopee_orders.csv")
shopee_df.to_csv(shopee_path, index=False)
print(f"-> Đã ghi {len(shopee_df):,} dòng vào: {shopee_path}")

# --- SÀN LAZADA (Thị phần 30%) ---
print("Đang xuất dữ liệu kênh Lazada...")
lazada_raw = df_merged[df_merged["channel"] == "lazada"].copy()
lazada_df = pd.DataFrame({
    "trade_order_id": "LZD_" + lazada_raw["order_id"].astype(str),
    "buyer_id": lazada_raw["customer_id"],
    "created_at": lazada_raw["order_purchase_timestamp"],
    "status": lazada_raw["order_status"].str.lower(),
    "price_amount": lazada_raw["total_amount"]
})
lazada_path = os.path.join(PROCESSED_DIR, "lazada_orders.csv")
lazada_df.to_csv(lazada_path, index=False)
print(f"-> Đã ghi {len(lazada_df):,} dòng vào: {lazada_path}")

# --- SÀN TIKTOK SHOP (Thị phần 25%) ---
print("Đang xuất dữ liệu kênh TikTok Shop...")
tiktok_raw = df_merged[df_merged["channel"] == "tiktokshop"].copy()
tiktok_df = pd.DataFrame({
    "order_id": "TTS_" + tiktok_raw["order_id"].astype(str),
    "user_id": tiktok_raw["customer_id"],
    "paid_time": tiktok_raw["order_purchase_timestamp"],
    "delivery_status": tiktok_raw["order_status"],
    "sku_sale_price": tiktok_raw["total_amount"]
})
tiktok_path = os.path.join(PROCESSED_DIR, "tiktok_orders.csv")
tiktok_df.to_csv(tiktok_path, index=False)
print(f"-> Đã ghi {len(tiktok_df):,} dòng vào: {tiktok_path}")

print("\n--- HOÀN THÀNH PHÂN TÁCH 3 KÊNH BÁN HÀNG THÀNH CÔNG ---")