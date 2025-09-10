###-----------Importing Libraries-----------###
import streamlit as st
from meteostat import Stations, Daily, Hourly, Monthly
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# from scipy.stats import shapiro
import numpy as np
# Establecer el estilo de los gráficos
sns.set_theme(style="whitegrid")
#Canvas ancho completo
st.set_page_config(layout="wide")


# titulo (añadir emoji de sol)
st.title('Cuando en marzo **mayea ☀️**,  en mayo NO **marcea 😎**')
# st.markdown(
#     """
#     # Cuando en marzo **mayea ☀️**  
#     # en mayo no **marcea 🥶**
#     """
# )



###-----------Defining Time Period-----------###
start = datetime(1985, 1, 1)
end = datetime(2025, 12, 31)
start_daily = datetime(2025, 6, 1)

#-----pasamos al castellano mejor-----#
# Obtener estación de Madrid (Cuatro Vientos)
station = '08222'  # Código de la estación Cuatro Vientos
# Descargar datos mensuales (incompletos, faltan los diarios que vienen a continuación)
data = Monthly(station, start, end).fetch()
# Descargar datos diarios
data_daily = Daily(station, start, end).fetch()
columnas = data_daily.columns.tolist()
# Rellenar NaN en todo el DataFrame (salvo índice)
data_daily = data_daily.fillna(0)
data_daily['tmax'] = data_daily['tmax'].astype(int)

# Añadir columnas de año, mes y nombre del mes
data_daily['year'] = data_daily.index.year
data_daily['month'] = data_daily.index.month
# data_daily['month_name'] = data_daily.index.month_name()

#numero de dias con max > 22
# Funcion para dia caluroso y frio
def mayeo(tmax, month):
    if tmax >= 20 and month == 3:
        return 1
    else:
        return 0
def marceo(tmax, month):
    if tmax < 18 and month == 5:
        return 1
    else:
        return 0

# Aplicar la función para contar días calurosos y fríos de marzo y mayo
data_daily['marzo_mayea'] = data_daily.apply(lambda row: mayeo(row['tmax'], row['month']), axis=1) #usamos lambda porque la funcion pose dos variables y hay que iterar a traves de x
data_daily['mayo_marcea'] = data_daily.apply(lambda row: marceo(row['tmax'], row['month']), axis=1)

# data_daily[data_daily['month']==5]
# data_daily
# Función para sumar 'prcp' y hacer media en el resto
def agg_prcp_sum_others_mean(df):
    funcs = {col: (np.sum if col in ['prcp', 'marzo_mayea', 'mayo_marcea'] else np.mean) for col in df.columns}
    df_agg = df.groupby(pd.Grouper(freq='ME')).agg(funcs)
    # Ajustar índice al primer día del mes
    df_agg.index = df_agg.index - pd.offsets.MonthEnd(1) + pd.Timedelta(days=1)
    return df_agg.round()
# Aplicar agregación
data_daily = agg_prcp_sum_others_mean(data_daily)
# Cambiar índice de fin de mes al primer día del mes
data_daily.index = data_daily.index - pd.offsets.MonthEnd(1) + pd.Timedelta(days=1)
data_daily[columnas] = data_daily[columnas].round()

# df= pd.concat([data, data_daily], axis=0)
# # 07156 Paris
# # 08222 Madrid (Cuatro Vientos)



# df

# subset de marzos y mayos
df_filtered = data_daily[data_daily['month'].isin([3, 5])]
#agrupar por año y mes y calcular la media
df_grouped = df_filtered.groupby('year')[['marzo_mayea', 'mayo_marcea']].sum().reset_index()

#                                         .agg({
#                                             # 'tmax': np.mean,
#                                             'marzo_mayea': np.sum,
#                                             'mayo_marcea': np.sum
#                                         }).reset_index()
# #sorting values
df_sorted = df_grouped.sort_values(by='year', ascending=True)

# Crear figura en streamlit
fig, ax = plt.subplots(figsize=(12, 6))

# Dibujar líneas con seaborn, reducri tamaño de los marcadores
sns.lineplot(
            data=df_sorted
             , x="year"
             , y="marzo_mayea"
             , marker="o"
             , markersize=5
             , label="#dias marzo caluroso"
             , color="#F5BCA0"
            #  , ax=ax
             )
sns.lineplot(
            data=df_sorted
             , x="year"
             , y="mayo_marcea"
             , marker="o"
             , markersize=5
             , label="#dias mayo frío"
             , color="#99B7CF"
            #  , ax=ax
             )

#mostrar grafico sin titulo
plt.ylabel('Número de Días')
plt.grid(False)
# Mostrar en Streamlit
st.pyplot(fig)



#info final
st.markdown(
    "<p style='text-align: right; font-style: italic;'>Estación Meteorológica de Madrid (Cuatro Vientos)</p>",
    unsafe_allow_html=True
)