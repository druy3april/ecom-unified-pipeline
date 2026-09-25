-- Chuẩn hóa schema sàn Shopee
with source as (
    select * from {{ source('raw_shopee', 'orders') }}
),

renamed as (
    select
        -- Khóa chính đơn hàng
        cast(order_sn as text) as order_id,
        cast(customer_id as text) as customer_id,
        
        -- Định danh kênh bán
        'Shopee' as channel_name,
        
        -- Chuẩn hóa timestamp
        cast(create_time as timestamp) as order_timestamp,
        cast(create_time as date) as order_date,
        
        -- Thống nhất trạng thái đơn hàng (chuyển về chữ thường snake_case)
        lower(trim(order_status)) as order_status,
        
        -- Chuẩn hóa giá trị tiền tệ
        cast(total_amount as numeric(15, 2)) as total_amount
    from source
)

select * from renamed