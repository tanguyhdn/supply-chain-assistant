with shipments as (
    select * from {{ ref('stg_scms_deliveries') }}
),

performance as (
    select
        shipment_id,
        country,
        product_group,
        sub_classification,
        shipment_mode,
        vendor,
        project_code,
        po_year,
        po_month,

        -- Métriques temporelles
        lead_time_days,
        delivery_delay_days,
        is_late_delivery,

        -- Catégorie de retard
        case
            when delivery_delay_days <= 0       then 'On Time or Early'
            when delivery_delay_days <= 14      then 'Minor Delay (1-14d)'
            when delivery_delay_days <= 30      then 'Moderate Delay (15-30d)'
            else                                     'Major Delay (30d+)'
        end                                          as delay_category,

        -- Métriques financières
        quantity,
        line_value_usd,
        freight_cost_usd,
        insurance_usd,
        total_landed_cost_usd,
        weight_kg,
        unit_price_usd,

        -- Ratio fret / valeur marchandise
        case
            when line_value_usd > 0
            then round(freight_cost_usd / line_value_usd, 4)
            else null
        end                                          as freight_to_value_ratio,

        -- Coût au kg
        case
            when weight_kg > 0
            then round(freight_cost_usd / weight_kg, 2)
            else null
        end                                          as cost_per_kg_usd,

        -- Classement urgence par mode de transport
        case shipment_mode
            when 'Air Charter' then 1
            when 'Air'         then 2
            when 'Truck'        then 3
            when 'Ocean'         then 4
            else 5
        end                                          as urgency_rank

    from shipments
)

select * from performance