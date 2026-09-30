/*
Model: dim_channels
Mục đích: Bảng chiều phân loại các kênh phân phối và tiếp thị
*/

with channels as (
    select 'Shopee' as channel_name, 'E-Commerce Marketplace' as channel_type
    union all
    select 'Lazada', 'E-Commerce Marketplace'
    union all
    select 'TikTok Shop', 'Social Commerce'
    union all
    select 'facebook_ads', 'Paid Social Marketing'
    union all
    select 'google_ads', 'Search & Shopping Marketing'
    union all
    select 'tiktok_ads', 'Short-form Video Marketing'
)

select 
    row_number() over (order by channel_name) as channel_key,
    channel_name,
    channel_type
from channels