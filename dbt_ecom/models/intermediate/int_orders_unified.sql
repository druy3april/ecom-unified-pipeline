/*
Model: int_orders_unified
Mục đích:
    - Hợp nhất (UNION ALL) toàn bộ dữ liệu đơn hàng đã chuẩn hóa từ 3 sàn:
      Shopee, Lazada, TikTok Shop.
    - Tạo trường khóa chính hợp nhất và phân loại trạng thái hoàn tất đơn hàng.
*/

with shopee as (
    select * from {{ ref('stg_shopee_orders') }}
),

lazada as (
    select * from {{ ref('stg_lazada_orders') }}
),

tiktok as (
    select * from {{ ref('stg_tiktok_orders') }}
),

unioned as (
    select * from shopee
    union all
    select * from lazada
    union all
    select * from tiktok
),

final as (
    select
        order_id,
        customer_id,
        channel_name,
        order_timestamp,
        order_date,
        order_status,
        total_amount,
        -- Cờ xác định đơn hàng thành công để tính doanh thu thực tế
        case 
            when order_status in ('delivered', 'completed') then 1
            else 0
        end as is_completed,
        -- Cờ xác định đơn hủy
        case 
            when order_status in ('canceled', 'cancelled', 'unavailable') then 1
            else 0
        end as is_canceled
    from unioned
)

select * from final