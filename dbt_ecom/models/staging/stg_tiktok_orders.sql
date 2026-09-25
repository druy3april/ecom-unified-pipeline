-- Chuẩn hóa schema sàn TikTok Shop
with source as (
    select * from {{ source('raw_tiktokshop', 'orders') }}
),

renamed as (
    select
        -- Khóa chính
        cast(order_id as text) as order_id,
        cast(user_id as text) as customer_id,
        
        -- Định danh kênh bán
        'TikTok Shop' as channel_name,
        
        -- Chuẩn hóa timestamp: TikTok dùng paid_time
        cast(paid_time as timestamp) as order_timestamp,
        cast(paid_time as date) as order_date,
        
        -- Trạng thái đơn hàng: TikTok dùng delivery_status
        lower(trim(delivery_status)) as order_status,
        
        -- Giá trị: TikTok dùng sku_sale_price
        cast(sku_sale_price as numeric(15, 2)) as total_amount
    from source
)

select * from renamed