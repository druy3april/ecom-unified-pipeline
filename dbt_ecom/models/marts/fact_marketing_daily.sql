/*
Model: fact_marketing_daily
Mục đích: Bảng Fact chi phí tiếp thị theo ngày và chiến dịch
*/

with marketing as (
    select * from {{ ref('stg_marketing_ads') }}
),

aggregated as (
    select
        date_day as marketing_date,
        ad_channel as channel_name,
        campaign_id,
        sum(ad_spend) as total_ad_spend,
        sum(impressions) as total_impressions,
        sum(clicks) as total_clicks
    from marketing
    group by 1, 2, 3
)

select
    md5(cast(marketing_date as text) || channel_name || campaign_id) as fact_marketing_key,
    marketing_date,
    channel_name,
    campaign_id,
    total_ad_spend,
    total_impressions,
    total_clicks,
    -- Tỷ lệ nhấp chuột (Click-Through Rate)
    case 
        when total_impressions > 0 
        then round(cast(total_clicks as numeric) / total_impressions, 4)
        else 0
    end as ctr,
    -- Chi phí trên mỗi lượt nhấp (Cost per Click)
    case 
        when total_clicks > 0 
        then round(total_ad_spend / total_clicks, 2)
        else 0
    end as cpc
from aggregated