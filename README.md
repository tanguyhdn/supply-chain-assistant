# 🚚 Supply Chain Analytics Assistant

> **[🔴 Live Demo](https://supply-chain-assistant-x3faq77guwqtqs7brcaubp.streamlit.app/)**

Assistant conversationnel Text-to-SQL appliqué à un dataset réel de 10 000+ livraisons
de produits médicaux humanitaires (USAID SCMS) — modélisation dbt en 3 couches,
BigQuery, API Claude.

---

## Contexte

Ce projet simule le système analytique d'une centrale d'approvisionnement humanitaire.
Il permet aux équipes non-techniques d'interroger les données supply chain
en langage naturel, sans écrire une seule ligne de SQL.

**Dataset source :** USAID Supply Chain Management System (SCMS) — open data
→ 10 324 lignes de commandes réelles de médicaments et dispositifs médicaux
→ 43 pays, 6 groupes de produits (ARV, ACT, HRDT, MRDT, ANTM, LLIN), 2006–2015

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Ingestion | dbt seed (CSV → BigQuery) |
| Modélisation | dbt Core (staging / intermediate / marts) |
| Stockage | Google BigQuery |
| LLM | Claude API (Anthropic) — claude-sonnet |
| Interface | Streamlit |
| Déploiement | Streamlit Cloud |

---

## Architecture

```
Dataset USAID SCMS (CSV)
        ↓ dbt seed
BigQuery (raw)
        ↓ dbt run
┌─────────────────────────────────────┐
│ staging/                            │
│   stg_scms_deliveries               │ ← nettoyage, typage, calcul délais
├─────────────────────────────────────┤
│ intermediate/                       │
│   int_shipment_performance          │ ← KPIs performance, catégorie retards
├─────────────────────────────────────┤
│ marts/                              │
│   fct_deliveries                    │ ← table de faits (grain: livraison)
│   agg_kpis_by_country_product       │ ← agrégats prêts pour le LLM
└─────────────────────────────────────┘
        ↓ Claude API (Text-to-SQL)
Streamlit App
```

---

## KPIs exposés

| KPI | Description |
|-----|-------------|
| `lead_time_days` | Délai PO → livraison réelle |
| `delivery_delay_days` | Écart livraison réelle vs planifiée |
| `on_time_delivery_rate_pct` | % livraisons dans les délais |
| `freight_to_value_ratio` | Ratio fret / valeur marchandise |
| `cost_per_kg_usd` | Coût transport au kilogramme |
| `total_landed_cost_usd` | Coût total (valeur + fret + assurance) |

---

## Exemples de questions

- *Quel pays a le taux de livraison à temps le plus faible ?*
- *Quel mode de transport génère le plus de retards majeurs ?*
- *Quels fournisseurs ont le lead time moyen le plus court ?*
- *Quelle est l'évolution du nombre de livraisons par année ?*
- *Comparer le coût fret moyen entre Air et Ocean pour les produits ARV*

---

## Lancer le projet en local

```bash
# 1. Cloner le repo
git clone https://github.com/tanguyhdn/supply-chain-assistant.git
cd supply-chain-assistant

# 2. Créer l'environnement Python
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configurer les secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Remplir avec vos clés GCP et Anthropic

# 4. Charger les données et builder les modèles dbt
cd supply_chain
dbt seed
dbt run
dbt test

# 5. Lancer l'app
cd ..
streamlit run app.py
```

---

## Structure du repo

```
supply-chain-assistant/
├── app.py                          ← interface Streamlit (chat UI)
├── llm.py                          ← logique Text-to-SQL (Claude API)
├── bigquery_client.py              ← connexion BigQuery + schéma
├── requirements.txt
├── supply_chain/                   ← projet dbt
│   ├── dbt_project.yml
│   ├── seeds/
│   │   └── scms_deliveries.csv     ← dataset USAID SCMS
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
└── .streamlit/
    └── secrets.toml                ← non committé
```