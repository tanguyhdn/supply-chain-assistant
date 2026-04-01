import anthropic
import streamlit as st
import re


def get_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def generate_sql(question: str, schema: str, project_id: str, dataset: str) -> str:
    client = get_client()

    system_prompt = f"""Tu es un expert en analyse de données supply chain humanitaire.
Tu génères des requêtes SQL BigQuery à partir de questions en langage naturel.

Règles strictes :
- Retourne UNIQUEMENT la requête SQL, sans explication, sans markdown, sans backticks
- Utilise toujours le nom complet des tables : `{project_id}.{dataset}.nom_table`
- Limite toujours les résultats à 100 lignes maximum avec LIMIT 100
- Utilise uniquement les tables et colonnes décrites dans le schéma
- Pour les agrégations par pays ou produit, préfère la table agg_kpis_by_country_product
- Pour les analyses détaillées par livraison, utilise fct_deliveries

Schéma des tables disponibles :
{schema}
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"Génère une requête SQL BigQuery pour répondre à cette question : {question}"
            }
        ],
        system=system_prompt
    )

    sql = message.content[0].text.strip()
    # Nettoyage au cas où Claude ajoute des backticks malgré la consigne
    sql = re.sub(r"```sql|```", "", sql).strip()
    return sql


def generate_answer(question: str, sql: str, results: str) -> str:
    client = get_client()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""Question : {question}

Requête SQL exécutée :
{sql}

Résultats :
{results}

Donne une réponse concise en français à la question, en t'appuyant sur les résultats."""
            }
        ]
    )

    return message.content[0].text.strip()