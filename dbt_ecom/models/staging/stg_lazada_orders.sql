-- Chuẩn hóa schema sàn Lazada
with source as (
    select * from {{ source('raw_lazada', 'orders') }}
),

renamed as (
    select
        -- Khóa chính: Lazada dùng trade_order_id
        cast(trade_order_id as text) as order_id,
        cast(buyer_id as text) as customer_id,
        
        -- Định danh kênh bán
        'Lazada' as channel_name,
        
        -- Chuẩn hóa timestamp: Lazada dùng created_at
        cast(created_at as timestamp) as order_timestamp,
        cast(created_at as date) as order_date,
        
        -- Trạng thái đơn hàng: Lazada dùng status
        lower(trim(status)) as order_status,
        
        -- Giá trị: Lazada dùng price_amount
        cast(price_amount as numeric(15, 2)) as total_amount
    from source
)

select * from renamed