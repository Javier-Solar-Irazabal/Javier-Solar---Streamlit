import streamlit as st
import pandas as pd
import requests
import json

##### para abrir la app en local

# cd C:\Users\ASUS\OneDrive\Escritorio\chatbot (esta es la ruta donde tengo el proyecto chatbot.py debéis poner la vuestra)
# python -m streamlit run chatbot.py

# acordaos de instalar streamlit (pip install streamlit), así como las demás librerías que se usan en el código (pandas, requests)

# Obtener la lista de modelos gratuitos disponibles desde OpenRouter
resp = requests.get("https://openrouter.ai/api/v1/models")
resp.raise_for_status()
data = resp.json()
# Filtrar modelos gratuitos, models ending with :free
free_models = [
    m["id"] for m in data["data"]
    if m["id"].endswith(":free")
]
# Definir las instrucciones del sistema para el modelo de IA, lo utilizaremos más adelante cuando configuremos las llamadas a los modelos. 
# Queremos definir cómo queremos que se comporte el modelo.
instrucciones = """Eres un analista financiero experto. 
                Te van a preguntar sobre el ticker seleccionado en el selectbox st.selectbox('Selecciona un ticker:', tickers).
                Incluye por favor siempre que sea posible comparativas sectoriales cuando muestres datos o calcules ratios. 
                Añade tambien al principio del todo nombre de compañia y a que sector pertenece"""


######## PANTALLA DE INICIO STREAMLIT ################
# Pantalla de inicio donde se pide la API KEY de OpenRouter
# Sidebar con input box para la API KEY
st.sidebar.header("Parametros")
# escribir en input box la api key, esto lo haremos en la app streamlit, no necesitas añadir la clave en el código
sidebar_api_key = st.sidebar.text_input("API Key de OpenRouter", type="password")
# si no ha escrito nada mostrar mensaje, el if not funciona de la siguiente manera: mientras no se haya introducido la clave se seguira mostranso el mensaje
# cuando hayamos introducido la clave, el if not sera false y se saltara este bloque, como veremos después.
if not sidebar_api_key:
    st.write("Por favor, introduce tu API KEY de OpenRouter en el sidebar para continuar.")
    #boton con enlace para conseguir API KEY
    st.sidebar.markdown("[Consigue tu API KEY gratuita en OpenRouter](https://openrouter.ai/)")
    # Redactamos disclaimer legal en la parte inferior de la app
    st.markdown(
        "<small>Esta aplicación tiene fines exclusivamente educativos y no constituye recomendación de inversión. La app no descarga ni almacena datos financieros de ningún tipo.</small>",
        unsafe_allow_html=True
    )
    st.stop()
# si no empieza por sk-or- mostrar error
if not sidebar_api_key.startswith("sk-or-"):
    st.error("API KEY no válida. Pon tu clave de OpenRouter en el código.")
    st.stop()


#####################################################

# Si todo va bien, mostramos la nueva pantalla de carga de archivos Excel

######## PANTALLA DE CARGA DE ARCHIVOS EXCEL ########
# ----------------SIDEBAR-ARCHIVOS-----------------------
#si ha escrito API 
if sidebar_api_key and sidebar_api_key.startswith("sk-or-"):
    #cargamos los archivos de balance, cashflow e income en el sidebar
    balance_file = st.sidebar.file_uploader("Balance.xlsx", type="xlsx")
    cash_file = st.sidebar.file_uploader("Cashflow.xlsx", type="xlsx")
    income_file = st.sidebar.file_uploader("Income.xlsx", type="xlsx")
    # selectbox con modelos free, nex-agi/deepseek-v3.1-nex-n1:free por defecto
    model = st.sidebar.selectbox("Selecciona un modelo de IA:", free_models, index=free_models.index("nex-agi/deepseek-v3.1-nex-n1:free") if "nex-agi/deepseek-v3.1-nex-n1:free" in free_models else 0) 
#------------------FUNCIÓN----------------------------
# Para que el modelo pueda leer los dataframes, los convertimos a texto en formato markdown
def df_to_text(df, name):
    try:
        return f"### {name}\n" + df.to_markdown(index=False) + "\n\n"
    except:
        return f"### {name}\n" + df.to_string() + "\n\n"
# -----------------CANVAS--------------------------------
#titulo principal
st.title("📊 Chatbot financiero")
#subtitulo
st.write("Powered by OpenRouter.ai")
####################################################

# Si se han cargado los 3 archivos, preparamos el contexto y mostramos la pantalla de formulación de pregunta

######## PANTALLA DE FORMULACIón DE PREGUNTA ########
# Si se ha completado la carga de los 3 archivos, los leemos y preparamos el contexto
if balance_file and cash_file and income_file:
    # Leer los archivos Excel en dataframes de pandas
    df_balance = pd.read_excel(balance_file, dtype=str)
    df_cash = pd.read_excel(cash_file, dtype=str)
    df_income = pd.read_excel(income_file, dtype=str)
    # Preparar listado de tickers
    tickers = df_balance['ticker'].unique().tolist()
    # Filtro situado encima del input de la pregunta
    ticker_seleccionado = st.selectbox("Selecciona un ticker:", tickers)
    # Filtramos los dataframes por el ticker seleccionado
    ##### PARTE IMPORTANTE: filtramos los dataframes por el ticker seleccionado para que el contexto no sea demasiado grande y el modelo pueda manejarlo.
    df_balance = df_balance[df_balance['ticker'] == ticker_seleccionado]
    df_cash = df_cash[df_cash['ticker'] == ticker_seleccionado]
    df_income = df_income[df_income['ticker'] == ticker_seleccionado]
    ##### PARTE IMPORTANTE: DEFINIR CONTEXTO
    # El contexto proporciona información adicional sobre la situación,
    # tema o datos que queremos que el modelo tenga en cuenta al responder, en este caso los dataframes que provienen de los archivos Excel.
    # Creamos el contexto combinando los 3 dataframes convertidos a texto
    contexto = (
        df_to_text(df_balance, "Balance") +
        df_to_text(df_cash, "Cashflow") +
        df_to_text(df_income, "Income Statement")
    )
    # Input box de la pregunta/prompt
    pregunta = st.text_input("Tu pregunta:")
    # Una vez realizada la pregunta, preparamos el payload y hacemos la llamada a OpenRouter para que se conecte al modelo y devuelva la respuesta
    if st.button("Preguntar") and pregunta.strip():
        ##### PAYLOAD Y LLAMADA A OPENROUTER #####
        # el PAYLOAD es un diccionario que contiene todos los datos que enviaremos a la API.
        # Incluye:
        # - El modelo a usar
        # - El historial de mensajes (instrucciones + pregunta del usuario)
        payload = {
            "model": model,  # modelo FREE elegido anteriormente
            "messages": [
                {"role": "system", "content": instrucciones}, # lo que hemos preparado al principio
                {"role": "user", "content": contexto + "\nPregunta: " + pregunta} # pregunta del usuario + contexto (pregunta en base a estos datos que te ofrezco)
            ]
        }
        headers = {
            "Authorization": f"Bearer {sidebar_api_key}",  ##Nunca compartas tu API Key públicamente!!!!
            "Content-Type": "application/json"
        }
        try:
            # Llamada POST a la API de OpenRouter
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            ##### RESPUESTA A LA PREGUNTA #####
            # Convertimos la respuesta en un diccionario de Python
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
            # Respuesta del modelo mostrada en pantalla
            st.subheader("Respuesta:")
            # Mostrar la respuesta que se ha obtenido del modelo en el paso previo
            st.write(respuesta)

        except Exception as e:
            st.error(f"Error llamando a OpenRouter: {e}")

else:
    st.info("Sube los 3 archivos Excel para empezar.")


# Redactamos disclaimer legal en la parte inferior de la app
st.markdown(
    "<small>Esta aplicación tiene fines exclusivamente educativos y no constituye recomendación de inversión. La app no descarga ni almacena datos financieros de ningún tipo.</small>",
    unsafe_allow_html=True
)
