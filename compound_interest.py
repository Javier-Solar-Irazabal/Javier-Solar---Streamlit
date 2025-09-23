import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd 
st.set_page_config(layout="wide")

# ---- Sidebar ----
st.sidebar.title("Investment Planner")
#description
st.sidebar.header("Input Parameters")
st.sidebar.markdown("""Select the parameters for your 30 years investment plan and see how it grows over time with compound interest.""")
#slicers
x = st.sidebar.slider("Monthly Investment ($)", min_value=100, max_value=1000, value=500, step=100)
n  = 12
P = x * n
# risk tolerance [low, medium, high]
r = st.sidebar.slider("Annual Interest Rate (%)", min_value=3.0, max_value=8.0, value=5.0, step=0.5) / 100
# risk profile [conservative, balanced, aggressive]
if r <= 4.0 / 100:
    risk_profile = "Conservative"
elif r <= 6.0 / 100:
    risk_profile = "Balanced"
else:
    risk_profile = "Aggressive"
# summary
st.sidebar.markdown(f"""**{risk_profile} risk profile selected.**""")
st.sidebar.markdown(f"""You have selected an annual investment of **${P}** with an annual interest rate of **{r*100}%**""")
st.sidebar.markdown(f"""**Assumption:** you get a salary raise every 5 years and you are willing to increase your monthly invested amount 10%""")

# ---- loading the data ----

t = 30

def compound_interest_cum(P, r, n, t):
    A = P * (1 + r)**(t)
    return A

year = datetime.now().year
base = 0
yearly_investment_cum = 0
years = []
values = []
pes = []
yearly_investment = []

# calculating compound interest with loop
for i in range(1,t+1):
    #calculating yield for current iteration + base
    current_year = compound_interest_cum(P, r, n, 1)
    # calculating yield of cumulative base
    if i > 1:
        base = compound_interest_cum(base, r, n, 1)
    #increasing P every 5 years by 10%
    if i % 5 == 0:
        P *= 1.1        
    # year
    year += 1
    # suming up current year + base
    base += current_year
    yearly_investment_cum += P
    years.append(year)
    values.append(base)
    yearly_investment.append(yearly_investment_cum)
    pes.append(P)
    print(f"Year {i}: ${base:,.2f}")

print(P * t)

#creating df
df = pd.DataFrame({"Year": years
                   , "Value": values
                   , 'Yearly_Investment': pes
                   , "Yearly_Investment_cum": yearly_investment
                   })

# future value and total invested
future_value = df["Value"].iloc[-1]
total_invested = df["Yearly_Investment_cum"].iloc[-1]

# ---- Main panel ----
st.title("Investment Growth Over Time")
st.subheader("*Compound interest is the most powerful force in the universe.*")
# flatten the arrayss
x = df["Year"].to_numpy()
y = df["Value"].to_numpy()
z = df["Yearly_Investment_cum"].to_numpy()

plt.figure(figsize=(10,5))          
plt.plot(x
         , y
         , marker="o"
         , markersize=4
         , color="#6693B7"
         , linestyle="-")
plt.plot(x
         , z
         , marker="o"
         , markersize=4
         , color="#B3B3B3"
         , linestyle="-")
plt.grid(False)
#removing unwanted borders
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.show()  

# Create columns: 2/3 for gráfico, 1/3 for anotaciones

col1, col2= st.columns([4, 1.25])

with col1:
    st.pyplot(plt)
with col2:
    st.markdown(f"### Future Value: ${future_value:,.0f}")
    st.markdown(f"### Total Invested: ${total_invested:,.0f}")
    st.markdown(f"### Earnings: ${future_value - total_invested:,.0f}")
    st.markdown(f"### Earnings (%): {round((future_value/total_invested - 1)*100, 1)}%")


