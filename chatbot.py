import streamlit as st
import pandas as pd
import os
import openai

# Configurar API para OpenRouter
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("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")

st.title("📈 Chatbot financiero sobre tus Excel")

# Subida de ficheros Excel
uploaded1 = st.file_uploader("Sube balance.xlsx", type=["xlsx"])
uploaded2 = st.file_uploader("Sube cashflow.xlsx", type=["xlsx"])
uploaded3 = st.file_uploader("Sube income.xlsx", type=["xlsx"])

if uploaded1 and uploaded2 and uploaded3:
    df_balance = pd.read_excel(uploaded1, dtype=str)
    df_cashflow = pd.read_excel(uploaded2, dtype=str)
    df_income = pd.read_excel(uploaded3, dtype=str)

    # Convertir a texto (simplificado)
    def df_to_text(df, name):
        txt = f"### Datos de {name}\n"
        try:
            txt += df.to_markdown(index=False)
        except Exception:
            txt += df.to_csv(index=False)
        return txt + "\n\n"

    contexto = df_to_text(df_balance, "Balance") + df_to_text(df_cashflow, "Cashflow") + df_to_text(df_income, "Income Statement")

    user_question = st.text_input("Haz tu pregunta sobre las empresas / ratios / datos (ej: ¿Cuál es el debt-to-equity de TICKER X?)")

    if st.button("Preguntar") and user_question.strip():
        prompt = f"""
Eres un analista financiero. Aquí tienes los datos de tres tablas (Balance, Cashflow, Income Statement) en formato tabular:

{contexto}

Usa solo esos datos. Responde con claridad. Usuario pregunta: {user_question}
"""
        try:
            response = openai.ChatCompletion.create(
                model="openrouter/meta-llama/llama-3.3-8b-instruct:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.2
            )
            answer = response.choices[0].message.content
            st.subheader("Respuesta del chatbot:")
            st.write(answer)
        except Exception as e:
            st.error(f"Error llamando a la API: {e}")

else:
    st.info("Sube los tres ficheros Excel para comenzar.")
