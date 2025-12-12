import streamlit as st
import pandas as pd
import requests
import json


# Obtener la lista de modelos disponibles desde OpenRouter
resp = requests.get("https://openrouter.ai/api/v1/models")
resp.raise_for_status()
data = resp.json()

# Filtrar modelos gratuitos, models ending with :free
free_models = [
    m["id"] for m in data["data"]
    if m["id"].endswith(":free")
]


# --------- API KEY DIRECTA (SIN ENTORNOS) ---------
# API_KEY = "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"  # <-- pega aquí tu clave sk-or-...

#on sidebar input box with APIKEY text
st.sidebar.header("Parametros")
# escribit en input box la api key
# st.sidebar.text_input("API Key de OpenRouter", type="password")
sidebar_api_key = st.sidebar.text_input("API Key de OpenRouter", type="password")

if not sidebar_api_key:
    st.write("Por favor, introduce tu API KEY de OpenRouter en el sidebar para continuar.")
    #boton con enlace para conseguir API KEY
    st.sidebar.markdown("[Consigue tu API KEY gratuita en OpenRouter](https://openrouter.ai/)")
    st.stop()

if not sidebar_api_key.startswith("sk-or-"):
    st.error("API KEY no válida. Pon tu clave de OpenRouter en el código.")
    st.stop()

# --------------------------------------------------
#si ha escrito API y es correcta cargar canvas
if sidebar_api_key and sidebar_api_key.startswith("sk-or-"):
    balance_file = st.sidebar.file_uploader("Balance.xlsx", type="xlsx")
    cash_file = st.sidebar.file_uploader("Cashflow.xlsx", type="xlsx")
    income_file = st.sidebar.file_uploader("Income.xlsx", type="xlsx")
    # selectbox con modelos free, nex-agi/deepseek-v3.1-nex-n1:free por defecto
    model = st.sidebar.selectbox("Selecciona un modelo de IA:", free_models, index=free_models.index("nex-agi/deepseek-v3.1-nex-n1:free") if "nex-agi/deepseek-v3.1-nex-n1:free" in free_models else 0)
    # model = st.sidebar.selectbox("Selecciona un modelo de IA:", free_models, index=0)  
# --------------------------------------------------
st.title("📊 Chatbot financiero")
st.write("Powered by OpenRouter.ai")
# balance_file = st.file_uploader("Balance.xlsx", type="xlsx")
# cash_file = st.file_uploader("Cashflow.xlsx", type="xlsx")
# income_file = st.file_uploader("Income.xlsx", type="xlsx")

def df_to_text(df, name):
    try:
        return f"### {name}\n" + df.to_markdown(index=False) + "\n\n"
    except:
        return f"### {name}\n" + df.to_string() + "\n\n"

if balance_file and cash_file and income_file:
    df_balance = pd.read_excel(balance_file, dtype=str)
    df_cash = pd.read_excel(cash_file, dtype=str)
    df_income = pd.read_excel(income_file, dtype=str)
    #ticker para filtrar
    #listado de tickers
    tickers = df_balance['ticker'].unique().tolist()
    ticker_seleccionado = st.selectbox("Selecciona un ticker:", tickers)
    #filtramos los dataframes por el ticker seleccionado
    df_balance = df_balance[df_balance['ticker'] == ticker_seleccionado]
    df_cash = df_cash[df_cash['ticker'] == ticker_seleccionado]
    df_income = df_income[df_income['ticker'] == ticker_seleccionado]
    contexto = (
        df_to_text(df_balance, "Balance") +
        df_to_text(df_cash, "Cashflow") +
        df_to_text(df_income, "Income Statement")
    )

    pregunta = st.text_input("Tu pregunta:")

    if st.button("Preguntar") and pregunta.strip():

        payload = {
            "model": model,  # modelo FREE elegido
            "messages": [
                {"role": "system", "content": "Eres un analista financiero experto. Te van a preguntar sobre el ticker seleccionado en el selectbox st.selectbox('Selecciona un ticker:', tickers). Incluye por favor siempre que sea posible comparativas sectoriales cuando muestres datos o calcules ratios. Añade tambien al principio del todo nombre de compañia y a que sector pertenece"},
                {"role": "user", "content": contexto + "\nPregunta: " + pregunta}
            ]
        }


        headers = {
            "Authorization": f"Bearer {sidebar_api_key}",
            "Content-Type": "application/json"
        }

        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )

            data = r.json()

            # Modelos FREE a veces devuelven "choices", otras "data" o "results"
            if "choices" in data:
                respuesta = data["choices"][0]["message"]["content"]
            elif "data" in data:
                respuesta = data["data"][0]["message"]["content"]
            elif "results" in data:
                respuesta = data["results"][0]["message"]["content"]
            else:
                respuesta = json.dumps(data, indent=2)

            st.subheader("Respuesta:")
            st.write(respuesta)

        except Exception as e:
            st.error(f"Error llamando a OpenRouter: {e}")

else:
    st.info("Sube los 3 archivos Excel para empezar.")
