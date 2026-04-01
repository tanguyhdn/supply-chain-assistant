from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st
import pandas as pd


def get_bq_client():
    credentials = service_account.Credentials.from_service_account_file(
        st.secrets.get("GCP_KEY_PATH", "secrets/gcp-key.json")
    )
    return bigquery.Client(
        credentials=credentials,
        project=st.secrets["GCP_PROJECT_ID"]
    )


def run_query(sql: str) -> pd.DataFrame:
    client = get_bq_client()
    try:
        df = client.query(sql).to_dataframe()
        return df
    except Exception as e:
        raise Exception(f"Erreur BigQuery : {str(e)}")


def get_schema() -> str:
    return """
Tables disponibles dans BigQuery (dataset: supply_chain_marts) :

1. fct_deliveries
   - shipment_id (STRING) : identifiant unique de la livraison
   - country (STRING) : pays de destination
   - product_group (STRING) : groupe de produits — valeurs exactes : 'ARV', 'ACT', 'HRDT', 'MRDT', 'ANTM', 'LLIN'
   - sub_classification (STRING) : sous-catégorie du produit
   - shipment_mode (STRING) : mode de transport — valeurs exactes : 'Air', 'Air Charter', 'Ocean', 'Truck'
   - vendor (STRING) : nom du fournisseur
   - project_code (STRING) : code interne du projet (ex: '100-BJ-T30', '102-KE-T01')
   - po_year (INT) : année du bon de commande — peut être NULL si date source manquante
   - po_month (INT) : mois du bon de commande — peut être NULL si date source manquante
   - delay_category (STRING) : catégorie de retard — valeurs exactes : 'On Time or Early', 'Minor Delay (1-14d)', 'Moderate Delay (15-30d)', 'Major Delay (30d+)'
   - urgency_rank (INT) : rang d'urgence du mode de transport (1=Air Charter, 2=Air, 3=Truck, 4=Ocean)
   - is_late_delivery (BOOL) : true si livraison en retard
   - lead_time_days (INT) : délai entre PO et livraison réelle — peut être négatif ou NULL
   - delivery_delay_days (INT) : écart entre livraison réelle et planifiée
   - quantity (INT) : quantité livrée
   - line_value_usd (FLOAT) : valeur de la ligne en USD
   - freight_cost_usd (FLOAT) : coût de fret en USD — peut être NULL (fret inclus dans le prix)
   - total_landed_cost_usd (FLOAT) : coût total (valeur + fret + assurance)
   - weight_kg (FLOAT) : poids en kg — peut être NULL
   - unit_price_usd (FLOAT) : prix unitaire en USD
   - freight_to_value_ratio (FLOAT) : ratio fret / valeur marchandise
   - cost_per_kg_usd (FLOAT) : coût de transport au kilogramme

   Notes importantes :
   - Pour les analyses par vendor, toujours filtrer avec HAVING COUNT(*) >= 10 pour des résultats significatifs
   - lead_time_days peut être négatif (anomalies de saisie dans les données sources)

2. agg_kpis_by_country_product
   - country (STRING) : pays de destination
   - product_group (STRING) : groupe de produits
   - sub_classification (STRING) : sous-catégorie
   - po_year (INT) : année — peut être NULL
   - nb_shipments (INT) : nombre de livraisons
   - total_units (INT) : total unités livrées
   - total_weight_kg (FLOAT) : poids total en kg
   - total_value_usd (FLOAT) : valeur totale en USD
   - total_freight_usd (FLOAT) : coût fret total en USD
   - total_landed_cost_usd (FLOAT) : coût total landed
   - avg_unit_price_usd (FLOAT) : prix unitaire moyen
   - avg_lead_time_days (FLOAT) : délai moyen en jours
   - avg_delay_days (FLOAT) : retard moyen en jours
   - on_time_delivery_rate_pct (FLOAT) : taux de livraison à temps (%)
   - on_time_count (INT) : nombre de livraisons à temps
   - minor_delay_count (INT) : nombre de retards mineurs
   - moderate_delay_count (INT) : nombre de retards modérés
   - major_delay_count (INT) : nombre de retards majeurs

   Notes importantes :
   - Cette table a une ligne par combinaison (country, product_group, po_year)
   - Pour obtenir un KPI global par pays, toujours agréger avec AVG() ou SUM() selon la métrique
   - Utiliser SUM() pour les compteurs (nb_shipments, total_value_usd)
   - Utiliser AVG() pour les ratios et pourcentages (on_time_delivery_rate_pct, avg_lead_time_days)
"""