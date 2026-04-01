with deliveries as (
    select * from {{ ref('fct_deliveries') }}
),

aggregated as (
    select
        country,
        product_group,
        sub_classification,
        po_year,

        -- Volume
        count(*)                                                as nb_shipments,
        sum(quantity)                                           as total_units,
        round(sum(weight_kg), 1)                               as total_weight_kg,

        -- Financier
        round(sum(line_value_usd), 2)                          as total_value_usd,
        round(sum(freight_cost_usd), 2)                        as total_freight_usd,
        round(sum(total_landed_cost_usd), 2)                   as total_landed_cost_usd,
        round(avg(unit_price_usd), 4)                          as avg_unit_price_usd,

        -- Performance livraison
        round(avg(lead_time_days), 1)                          as avg_lead_time_days,
        round(avg(delivery_delay_days), 1)                     as avg_delay_days,
        round(
            100.0 * countif(is_late_delivery = false)
            / nullif(count(*), 0),
        1)                                                     as on_time_delivery_rate_pct,

        -- Répartition retards
        countif(delay_category = 'On Time or Early')           as on_time_count,
        countif(delay_category = 'Minor Delay (1-14d)')        as minor_delay_count,
        countif(delay_category = 'Moderate Delay (15-30d)')    as moderate_delay_count,
        countif(delay_category = 'Major Delay (30d+)')         as major_delay_count

    from deliveries
    group by country, product_group, sub_classification, po_year
)

select * from aggregated
order by po_year desc, total_value_usd desc