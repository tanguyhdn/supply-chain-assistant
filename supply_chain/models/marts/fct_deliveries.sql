with base as (
    select * from {{ ref('int_shipment_performance') }}
)

select
    -- Clés
    shipment_id,
    country,
    product_group,
    sub_classification,
    shipment_mode,
    vendor,
    project_code,
    po_year,
    po_month,

    -- Dimensions de performance
    delay_category,
    urgency_rank,
    is_late_delivery,

    -- Métriques temporelles
    lead_time_days,
    delivery_delay_days,

    -- Métriques financières
    quantity,
    line_value_usd,
    freight_cost_usd,
    total_landed_cost_usd,
    weight_kg,
    unit_price_usd,
    freight_to_value_ratio,
    cost_per_kg_usd

from base