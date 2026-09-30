/*
Model: fact_orders_daily
Mục đích: Bảng Fact tổng hợp số liệu giao dịch theo ngày và kênh bán
*/

with orders as (
    select * from {{ ref('int_orders_unified') }}
),

aggregated as (
    select
        order_date,
        channel_name,
        count(distinct order_id) as total_orders,
        sum(is_completed) as total_completed_orders,
        sum(is_canceled) as total_canceled_orders,
        -- Tổng doanh thu gộp (GMV)
        sum(total_amount) as gross_revenue,
        -- Doanh thu thực tế (chỉ tính đơn thành công)
        sum(case when is_completed = 1 then total_amount else 0 end) as net_revenue
    from orders
    group by 1, 2
)

select
    -- Tạo Surrogate Key cho Fact table
    md5(cast(order_date as text) || channel_name) as fact_order_key,
    order_date,
    channel_name,
    total_orders,
    total_completed_orders,
    total_canceled_orders,
    gross_revenue,
    net_revenue,
    -- Giá trị trung bình đơn hàng hoàn tất (AOV)
    case 
        when total_completed_orders > 0 
        then round(net_revenue / total_completed_orders, 2)
        else 0
    end as average_order_value
from aggregated