import streamlit as st
import pandas as pd
from bigquery_client import run_query, get_schema
from llm import generate_sql, generate_answer

st.set_page_config(
    page_title="Supply Chain Analytics Assistant",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Supply Chain Analytics Assistant")
st.caption("Interrogez les données de livraisons humanitaires en langage naturel")

# Exemples de questions
with st.expander("💡 Exemples de questions"):
    st.markdown("""
    - Quel pays a le taux de livraison à temps le plus faible ?
    - Quelle est la valeur totale des livraisons par pays ?
    - Quel mode de transport génère le plus de retards majeurs ?
    - Quels sont les 5 fournisseurs avec le lead time moyen le plus court (minimum 10 livraisons) ?
    - Comparer le coût fret moyen entre Air et Ocean pour les produits ARV
    - Quelle est l'évolution du nombre de livraisons par année ?
    """)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "dataframe" in message:
            st.dataframe(message["dataframe"], use_container_width=True)
        if "sql" in message:
            with st.expander("🔍 Requête SQL générée"):
                st.code(message["sql"], language="sql")

# Input utilisateur
if question := st.chat_input("Posez votre question sur les données supply chain..."):

    # Affichage de la question
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Génération de la réponse
    with st.chat_message("assistant"):
        with st.spinner("Génération de la requête SQL..."):
            try:
                schema = get_schema()
                project_id = st.secrets["GCP_PROJECT_ID"]
                dataset = st.secrets["BQ_DATASET"]

                # Génération SQL
                sql = generate_sql(question, schema, project_id, dataset)

                # Exécution BigQuery
                with st.spinner("Exécution sur BigQuery..."):
                    df = run_query(sql)

                # Réponse en langage naturel
                with st.spinner("Formulation de la réponse..."):
                    results_str = df.to_string(index=False, max_rows=20)
                    answer = generate_answer(question, sql, results_str)

                # Affichage
                st.markdown(answer)
                st.dataframe(df, use_container_width=True)
                with st.expander("🔍 Requête SQL générée"):
                    st.code(sql, language="sql")

                # Sauvegarde dans l'historique
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "dataframe": df,
                    "sql": sql
                })

            except Exception as e:
                error_msg = f"❌ Erreur : {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })