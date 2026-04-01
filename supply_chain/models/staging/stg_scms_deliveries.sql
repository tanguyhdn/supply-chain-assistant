with source as (
    select * from {{ source('supply_chain', 'scms_deliveries') }}
),

cleaned as (
    select
        -- Identifiants
        id                                                              as shipment_id,
        project_code,
        pq_number,
        po_so_number,
        asn_dn_number,

        -- Géographie & logistique
        country,
        managed_by,
        fulfill_via,
        vendor_inco_term,
        shipment_mode,

        -- Dates (formats mixtes selon la colonne)
        safe.parse_date('%m/%d/%y', pq_first_sent_to_client_date)      as pq_sent_date,
        safe.parse_date('%m/%d/%y', po_sent_to_vendor_date)            as po_date,
        safe.parse_date('%d-%b-%y', scheduled_delivery_date)           as scheduled_delivery_date,
        safe.parse_date('%d-%b-%y', delivered_to_client_date)          as actual_delivery_date,
        safe.parse_date('%d-%b-%y', delivery_recorded_date)            as recorded_date,

        -- Délais calculés
        date_diff(
            safe.parse_date('%d-%b-%y', delivered_to_client_date),
            safe.parse_date('%m/%d/%y', po_sent_to_vendor_date),
            day
        )                                                               as lead_time_days,

        date_diff(
            safe.parse_date('%d-%b-%y', delivered_to_client_date),
            safe.parse_date('%d-%b-%y', scheduled_delivery_date),
            day
        )                                                               as delivery_delay_days,

        -- Flag retard
        case
            when safe.parse_date('%d-%b-%y', delivered_to_client_date)
                 > safe.parse_date('%d-%b-%y', scheduled_delivery_date)
            then true
            else false
        end                                                             as is_late_delivery,

        -- Produit
        product_group,
        sub_classification,
        vendor,
        item_description,
        molecule_test_type,
        brand,
        dosage,
        dosage_form,
        unit_of_measure,
        manufacturing_site,
        first_line_designation,

        -- Colonnes numériques — cast safe pour les valeurs texte
        cast(nullif(trim(line_item_quantity), '') as integer)           as quantity,
        safe_cast(line_item_value as float64)                           as line_value_usd,
        safe_cast(pack_price as float64)                                as pack_price_usd,
        safe_cast(unit_price as float64)                                as unit_price_usd,
        safe_cast(weight_kilograms as float64)                          as weight_kg,
        safe_cast(freight_cost_usd as float64)                          as freight_cost_usd,
        safe_cast(line_item_insurance_usd as float64)                   as insurance_usd,

        -- Landed cost total
        round(
            coalesce(safe_cast(line_item_value as float64), 0)
            + coalesce(safe_cast(freight_cost_usd as float64), 0)
            + coalesce(safe_cast(line_item_insurance_usd as float64), 0),
        2)                                                              as total_landed_cost_usd,

        -- Dimensions temporelles
        extract(year from safe.parse_date('%m/%d/%y', po_sent_to_vendor_date))  as po_year,
        extract(month from safe.parse_date('%m/%d/%y', po_sent_to_vendor_date)) as po_month

    from source
    where id is not null
      and country is not null
      and delivered_to_client_date is not null
      and po_sent_to_vendor_date is not null
)

select * from cleaned