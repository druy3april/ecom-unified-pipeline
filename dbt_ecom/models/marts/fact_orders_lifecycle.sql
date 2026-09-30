{{
    config(
        materialized='table',
        schema='marts'
    )
}}

with unified_orders as (
    select * from {{ ref('int_orders_unified') }}
),

final as (
    select
        order_id,
        channel_name,
        order_status,
        order_date,
        total_amount,
        -- Logic đánh dấu trạng thái hoàn tất đơn hàng
        case
            when lower(order_status) in ('delivered', 'completed', 'success') then true
            else false
        end as is_completed,

        case
            when lower(order_status) in ('cancelled', 'canceled', 'returned') then true
            else false
        end as is_cancelled,

        -- Snapshot audit metadata (timestamp lúc build mart)
        current_timestamp as mart_calculated_at

    from unified_orders
)

select * from final