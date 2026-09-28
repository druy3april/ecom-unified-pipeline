{% snapshot snp_orders_status %}

{{
    config(
      target_schema='snapshots',
      unique_key='order_id',
      strategy='check',
      check_cols=['order_status'],
      invalidate_hard_deletes=True
    )
}}

select
    order_id,
    order_status,
    channel_name,
    order_date
from {{ ref('int_orders_unified') }}

{% endsnapshot %}