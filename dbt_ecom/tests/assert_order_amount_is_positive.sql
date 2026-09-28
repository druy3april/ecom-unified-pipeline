-- Test này đảm bảo không có đơn hàng nào bị lỗi tiền âm (< 0)
-- Nếu có dòng nào trả về -> Test FAIL
select
    order_id,
    total_amount
from {{ ref('fact_orders_lifecycle') }}
where total_amount < 0