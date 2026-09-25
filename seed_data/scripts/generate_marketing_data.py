"""
Script: generate_marketing_data.py
Mục đích:
    - Lấy khoảng thời gian thực tế từ tập đơn hàng Olist (min date đến max date).
    - Sinh dữ liệu chi phí quảng cáo hàng ngày (Daily Ad Spend) cho 3 kênh:
        + Facebook Ads
        + Google Ads
        + TikTok Ads
    - Áp dụng các quy luật thị trường thực tế:
        + Tăng ngân sách vào cuối tuần (Thứ 7, Chủ Nhật)
        + Tăng đột biến (Spike) vào các đợt Siêu Sale (Ngày đôi: 9/9, 10/10, 11/11, 12/12)
        + Tỷ lệ Click-Through-Rate (CTR) và chi phí mỗi click (CPC) hợp lý.
    - Xuất file kết quả ra seed_data/processed/marketing_ad_spend.csv
"""

import os
import pandas as pd
import numpy as np

# 1. Đường dẫn thư mục
RAW_DIR = "seed_data/raw"
PROCESSED_DIR = "seed_data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("--- BẮT ĐẦU SINH DỮ LIỆU MARKETING ADS SPEND ---")

# 2. Xác định khoảng thời gian chạy ads dựa trên thời gian đơn hàng thật
orders_file = os.path.join(RAW_DIR, "olist_orders_dataset.csv")
df_orders = pd.read_csv(orders_file, usecols=["order_purchase_timestamp"])
df_orders["order_purchase_timestamp"] = pd.to_datetime(df_orders["order_purchase_timestamp"])

min_date = df_orders["order_purchase_timestamp"].min().date()
max_date = df_orders["order_purchase_timestamp"].max().date()
print(f"Khoảng thời gian chiến dịch: Từ {min_date} đến {max_date}")

# Tạo danh sách các ngày liên tục
date_range = pd.date_range(start=min_date, end=max_date, freq="D")

# 3. Cấu hình các kênh quảng cáo và chiến dịch mẫu
channels_config = {
    "facebook_ads": {
        "campaigns": ["FB_Brand_Awareness", "FB_Retargeting_Catalog", "FB_Conversion_FlashSale"],
        "base_budget": (500000, 2000000),      # Ngân sách cơ bản 500k - 2tr VNĐ/ngày
        "cpm_range": (30000, 70000),           # Chi phí 1000 lượt hiển thị (CPM)
        "ctr_range": (0.015, 0.035)            # Tỷ lệ click (1.5% - 3.5%)
    },
    "google_ads": {
        "campaigns": ["GG_Search_Brand", "GG_Search_Generic_SKU", "GG_Shopping_PerformanceMax"],
        "base_budget": (800000, 2500000),      # Ngân sách cơ bản 800k - 2.5tr VNĐ/ngày
        "cpm_range": (40000, 90000),
        "ctr_range": (0.030, 0.060)            # Google Search CTR thường cao hơn
    },
    "tiktok_ads": {
        "campaigns": ["TT_Video_Shopping_Live", "TT_Spark_Ads_KOL", "TT_Traffic_Store"],
        "base_budget": (400000, 1800000),      # Ngân sách cơ bản 400k - 1.8tr VNĐ/ngày
        "cpm_range": (20000, 50000),           # TikTok CPM thường rẻ hơn
        "ctr_range": (0.010, 0.025)
    }
}

np.random.seed(42)
records = []

# 4. Vòng lặp duyệt qua từng ngày và từng chiến dịch
for single_date in date_range:
    is_weekend = single_date.weekday() >= 5  # Thứ 7 hoặc Chủ Nhật
    # Kiểm tra ngày đôi (Siêu sale: 9/9, 10/10, 11/11, 12/12)
    is_mega_sale = (single_date.day == single_date.month) and (single_date.month in [9, 10, 11, 12])

    for channel_name, config in channels_config.items():
        for campaign in config["campaigns"]:
            # Tính hệ số ngân sách theo hành vi thị trường
            multiplier = 1.0
            if is_weekend:
                multiplier *= 1.35  # Cuối tuần tăng 35% ngân sách
            if is_mega_sale:
                multiplier *= 3.00  # Ngày sale đôi x3 ngân sách

            # Sinh chi phí quảng cáo (ad_spend)
            base_min, base_max = config["base_budget"]
            ad_spend = int(np.random.uniform(base_min, base_max) * multiplier)

            # Sinh CPM (Cost per 1,000 Impressions)
            cpm = np.random.uniform(*config["cpm_range"])
            # Tính số lượt hiển thị (Impressions)
            impressions = int((ad_spend / cpm) * 1000)

            # Sinh CTR và tính số lượt click thực tế
            ctr = np.random.uniform(*config["ctr_range"])
            clicks = int(impressions * ctr)

            # Tính CPC (Cost per Click) trung bình
            cpc = round(ad_spend / clicks, 2) if clicks > 0 else 0

            records.append({
                "campaign_id": campaign,
                "ad_channel": channel_name,
                "date": single_date.strftime("%Y-%m-%d"),
                "ad_spend": ad_spend,
                "impressions": impressions,
                "clicks": clicks,
                "cpc": cpc
            })

df_marketing = pd.DataFrame(records)

# 5. Xuất file kết quả
output_path = os.path.join(PROCESSED_DIR, "marketing_ad_spend.csv")
df_marketing.to_csv(output_path, index=False)

print(f"-> Đã sinh thành công {len(df_marketing):,} bản ghi chi phí Ads.")
print(f"-> Đã ghi file kết quả vào: {output_path}")
print("--- HOÀN THÀNH BƯỚC SINH DỮ LIỆU MARKETING ---")