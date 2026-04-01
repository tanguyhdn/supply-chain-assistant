import pandas as pd

input_path = "supply_chain/seeds/SCMS_Delivery_History_Dataset.csv"
output_path = "supply_chain/seeds/scms_deliveries.csv"

df = pd.read_csv(input_path)

df.columns = [
    "id",
    "project_code",
    "pq_number",
    "po_so_number",
    "asn_dn_number",
    "country",
    "managed_by",
    "fulfill_via",
    "vendor_inco_term",
    "shipment_mode",
    "pq_first_sent_to_client_date",
    "po_sent_to_vendor_date",
    "scheduled_delivery_date",
    "delivered_to_client_date",
    "delivery_recorded_date",
    "product_group",
    "sub_classification",
    "vendor",
    "item_description",
    "molecule_test_type",
    "brand",
    "dosage",
    "dosage_form",
    "unit_of_measure",
    "line_item_quantity",
    "line_item_value",
    "pack_price",
    "unit_price",
    "manufacturing_site",
    "first_line_designation",
    "weight_kilograms",
    "freight_cost_usd",
    "line_item_insurance_usd"
]

df.to_csv(output_path, index=False)
print(f"✅ {len(df)} lignes → {output_path}")
print(f"Colonnes : {list(df.columns)}")