##"""""""""""importing libraries"""""""""##

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import datetime as dt
from fredapi import Fred

# credentials for FED databank API
fred = Fred(api_key='cd9da7549b07c0b28b7882bd7a016187')

##""""""""""Getting the data"""""""""##

###################################################
#####--YIELD-CURVE-INVERSION--#####################
###################################################

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import datetime as dt
from fredapi import Fred

##""""""""""Getting the data"""""""""##

###################################################
#####--YIELD-CURVE-INVERSION--#####################
###################################################

fred = Fred(api_key='cd9da7549b07c0b28b7882bd7a016187')

# Definir fechas
start_date = "1990-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')

# Obtener datos desde FRED
dgs10 = fred.get_series("DGS10", start_date, end_date)  # 10Y Treasury Bond
dgs3mo = fred.get_series("DGS3MO", start_date, end_date)  # 3M Treasury Bill

# Crear DataFrame
df_fed = pd.DataFrame({
    'Date': dgs10.index,
    '10Y US Treasury Bond': dgs10.values,
    '3M Treasury Bill': dgs3mo.values
}).dropna()

# Calcular la diferencia de rendimiento
df_fed['Yield Spread'] = df_fed["10Y US Treasury Bond"] - df_fed["3M Treasury Bill"]
# Reset index to convert the Date from index to a column
df = df_fed#.reset_index()
# Assuming df is already defined in your code
df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
#100 days chart
hundred_days = datetime.now() - timedelta(days=100)
df_hundred = df[df['Date']>=hundred_days]

# Set up the plotting environment
fig1=plt.figure(figsize=(10,5))

# Plot Yield Spread with shading
df['Positive Spread'] = df['Yield Spread'].apply(lambda x: x if x > 0 else 0)
df['Negative Spread'] = df['Yield Spread'].apply(lambda x: x if x < 0 else 0)

# Plot Yield Spread with shading
for i in range(1, len(df)):
    x = [df['Date'].iloc[i-1], df['Date'].iloc[i]]
    y = [df['Yield Spread'].iloc[i-1], df['Yield Spread'].iloc[i]]
    if y[0] < 0 or y[1] < 0:
        color = 'lightcoral'
        plt.plot(x, y, color=color, alpha=0.1)  
plt.fill_between(df['Date'], df['Negative Spread'], color='lightcoral', alpha=0.5)
# Plot 3M Treasury Bill
sns.lineplot(x='Date', y='3M Treasury Bill', data=df, color='lightblue',  label='3M Bill Yield')
# Plot 10Y US Treasury Bond
sns.lineplot(x='Date', y='10Y US Treasury Bond', data=df, color='#004B87', label='10Y Bond Yield')

# Annotate last values
# last_index = df.index[-1]
# plt.annotate(f'{df["3M Treasury Bill"].iloc[-1]:.2f}', 
#              (df['Date'].iloc[-1], df['3M Treasury Bill'].iloc[-1]),
#              textcoords="offset points",
#              fontsize = 8,
#              xytext=(10, 0),
#              ha='left',
#              color='#004B87')
# plt.annotate(f'{df["10Y US Treasury Bond"].iloc[-1]:.2f}', 
#              (df['Date'].iloc[-1], df['10Y US Treasury Bond'].iloc[-1]),
#              textcoords="offset points",
#              fontsize = 8,
#              xytext=(10, 0),
#              ha='left',
#              color='#004B87')

# Define the positions of the ticks and their labels for the y-axis
y_tick_positions = [-3, 0, 8]
y_tick_labels = ['-3%', '0%', '8%']

# Add text boxes below the x-axis where values are < 0
# we want to use this comments to highlight recession which take place exactly after the yield curve inversion
for i in range(1, len(df)):
    date = df['Date'].iloc[i]
    y = df['Yield Spread'].iloc[i]
    if y < 0:
        label = ''
        label_ = ''
        if date.year == 2000:
            label = 'Dot-com Bubble'
        elif date.year == 2006:
            label = 'SubPrime Crisis'
        elif date.year == 2019:
            label = 'Covid-19'
        elif date.year == 2023:   ## labels for the current yield curve inversion
            label_ = '?????'
        if label:
            plt.text(date, -1, label,  # Adjust the y-value to position text below the x-axis
                     ha='center', va='top', fontsize=7,
                     color='gray',
                     bbox=dict(facecolor='white', alpha=1, edgecolor='none'))
        if label_:
            plt.text(date, -2, label_,  # Adjust the y-value to position text below the x-axis
                     ha='center', va='top', fontsize=15,
                     color='gray',
                     bbox=dict(facecolor='white', alpha=1, edgecolor='none'))

# Remove the frame (spines)
for spine in plt.gca().spines.values():
    spine.set_visible(False)

# Customize the plot
plt.title('Yield Curve Inversion', fontsize=12, loc='left', color='#004B87')
# No axis' labels
plt.xlabel('')
plt.ylabel('')
# Apply tight layout to remove extra padding
plt.tight_layout()
# Display legend with no frame and smaller font size
plt.legend(frameon=False, fontsize=7)
# Set the ticks on the y-axis
plt.yticks(ticks=y_tick_positions, labels=y_tick_labels)


# Set up the plotting environment for 100 days chart
fig2=plt.figure(figsize=(8,6.5))
# Plot 3M Treasury Bill
sns.lineplot(x='Date', y='3M Treasury Bill', data=df_hundred, color='lightblue',  label='3M Bill Yield')
# Plot 10Y US Treasury Bond
sns.lineplot(x='Date', y='10Y US Treasury Bond', data=df_hundred, color='#004B87', label='10Y Bond Yield')
# Remove the frame (spines)
for spine in plt.gca().spines.values():
    spine.set_visible(False)
# Customize the plot
plt.title('Last 100 days', fontsize=14, loc='left', color='#004B87')
# No axis' labels
plt.xlabel('')
plt.ylabel('')
# Apply tight layout to remove extra padding
plt.tight_layout()
plt.legend('', frameon=False)
# Define the positions of the ticks and their labels for the y-axis
y_tick_positions_hundred = [4,5]
y_tick_labels_hundred = ['4%', '5%']
# Set the ticks on the y-axis
plt.yticks(ticks=y_tick_positions_hundred, labels=y_tick_labels_hundred)

#######################################
##--JOB-LESS-CLAIMS####################
#######################################

# launching FRED
# Retrieve initial jobless claims data (FRED series ID: ICSA)
jobless_claims = fred.get_series('ICSA')
# Convert the data to a DataFrame
jobless_claims_df = pd.DataFrame(jobless_claims, columns=['Jobless Claims'])
jobless_claims_df.index.name = 'Date'
jobless_claims_df= jobless_claims_df.reset_index()
jobless_claims_df['Date']=pd.to_datetime(jobless_claims_df['Date']
                                         , format='%Y-%m-%d')
# Get today's date
today = datetime.today()
# Calculate the date two years ago
two_years_ago = today - timedelta(days=3*365)
# Filter for the last two years
last_two_years_df = jobless_claims_df[jobless_claims_df['Date'] >= two_years_ago]

#### Ploting jobless claims
# Set the plot size (optional)
fig3=plt.figure(figsize=(10, 3))

# Create a line chart using Seaborn
sns.lineplot(x='Date', y='Jobless Claims', data=last_two_years_df)

# Add labels and a title
plt.title('Job Less Claims', fontsize=10, loc='left', color='#004B87')
plt.xlabel('Date')
plt.ylabel('Jobless Claims')
#Removing axes for better visualization 
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_color('black')
plt.gca().spines['bottom'].set_color('black')
#Adjusting axis size
plt.xticks(fontsize=5)  
plt.yticks(fontsize=5)
#Removing axis titles
plt.xlabel('') #x axis
plt.ylabel('') #y axis
# Remove the frame (spines)
for spine in plt.gca().spines.values():
    spine.set_visible(False)
# Display the chart
plt.xticks(rotation=45)  # Rotate x-axis labels if needed
plt.show()

##""""""""""Populating the dashboard"""""""""##

#######################################
##--STREAMLIT-DASHBOARD--##############
#######################################

st.set_page_config(layout="wide")

# Set the title for the dashboard
st.markdown("<h1 style='color: #004B87; font-size: 50px;'>Recession Upcoming?</h1>", unsafe_allow_html=True)

####FIRST PART YIELD CURVE
# Create two columns: one for the chart (larger) and one for the text (smaller)
col1, col2, col3 = st.columns([2.5, 1.5, 1])  # 4/1 split to make the chart larger

with col1:
    # Display fig1 (yield curve) plot in the first column (larger column)
    st.pyplot(fig1)

with col2: 
    # Display fig2 (yield curve 100 days) plot in the second column (medium column)
    st.pyplot(fig2)

with col3:
    # Add the explanation text in the second column with smaller font size
    st.markdown("""
    <div style="font-size:12px; color: darkgray; margin-top: 50px;">
    <p>An inverted yield curve is a clear signal of an impending recession. It occurs when short-term interest rates are higher than long-term rates, reflecting pessimism about future economic growth. 
    </div>
    <div style="font-size:12px; color: darkgray;">
    <p>Historically, every red-shaded period on the chart has preceded a recession, followed by a downturn in major stock indexes. 
    </div>
     <div style="font-size:12px; color: darkgray;">   
    <p>Once the curve inversion reverses, it typically marks the onset of the economic downturn.
    """, unsafe_allow_html=True)

######
# Add some blank separation between the sections
st.markdown("<div style='margin:60px 0;'></div>", unsafe_allow_html=True)
######

###SECOND PART JOBLESS CLAIMS
col4, col5 = st.columns([4,1])
with col4:
    # Display fig1 (yield curve) plot in the first column (larger column)
    st.pyplot(fig3)
with col5:
    # Add the explanation text in the second column with smaller font size
    st.markdown("""
    <div style="font-size:12px; color: darkgray; margin-top: 50px;">
    <p>Nevertheless, since the jobless claims seems to be stable in the recent years, we cannot say that there is a recession ahead yeat. 
    </div>
    <div style="font-size:12px; color: darkgray;">
    <p>Despite the yield curve anomaly, we need to see deflationary levers in action, such as job market inbalances, to certify the economic downturn 
    """, unsafe_allow_html=True) 

