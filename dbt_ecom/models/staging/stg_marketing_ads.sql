-- Chuẩn hóa chi phí quảng cáo
with source as (
    select * from {{ source('raw_marketing', 'ad_spend') }}
),

renamed as (
    select
        cast(campaign_id as text) as campaign_id,
        cast(ad_channel as text) as ad_channel,
        cast(date as date) as date_day,
        cast(ad_spend as numeric(15, 2)) as ad_spend,
        cast(impressions as integer) as impressions,
        cast(clicks as integer) as clicks,
        cast(cpc as numeric(10, 2)) as cpc
    from source
)

select * from renamed