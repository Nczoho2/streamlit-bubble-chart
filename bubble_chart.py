import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(layout="wide")
st.title("Trading Bubble Chart (Buy vs Sell Volume with Price Levels)")

@st.cache_data
def generate_simulated_data(buckets=200, base_price=4750):
    start_time = datetime(2022, 1, 3, 9, 0, 0)
    price = base_price
    data = []
    for i in range(buckets):
        timestamp = start_time + timedelta(seconds=i * 3)
        price_change = random.choices([-2, -1, 0, 1, 2], weights=[1, 3, 4, 3, 1])[0]
        price += price_change
        market_buy = random.randint(0, 15)
        market_sell = random.randint(0, 15)
        pending_buy = random.randint(10, 30)
        pending_sell = random.randint(10, 30)
        buy_vol = market_buy + pending_buy
        sell_vol = market_sell + pending_sell
        total_vol = buy_vol + sell_vol
        data.append({
            'bucket': timestamp,
            'price': price,
            'market_buy_volume': market_buy,
            'market_sell_volume': market_sell,
            'pending_buy_volume': pending_buy,
            'pending_sell_volume': pending_sell,
            'buy_volume': buy_vol,
            'sell_volume': sell_vol,
            'total_volume': total_vol
        })
    return pd.DataFrame(data)

sim_df = generate_simulated_data()
window_size = st.slider("Select number of 3s intervals to display:", min_value=20, max_value=200, value=80, step=10)
data_window = sim_df.tail(window_size).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(18, 10))
x = np.arange(len(data_window))
sizes = data_window['total_volume'] * 20

for i, row in data_window.iterrows():
    total = row['total_volume']
    if total == 0:
        continue
    buy_ratio = row['buy_volume'] / total
    radius = np.sqrt(sizes[i]) / 10
    center_x = i
    center_y = row['price']
    wedge1 = mpatches.Wedge((center_x, center_y), radius, 90, 90 + 360 * buy_ratio, color='green')
    wedge2 = mpatches.Wedge((center_x, center_y), radius, 90 + 360 * buy_ratio, 450, color='red')
    ax.add_patch(wedge1)
    ax.add_patch(wedge2)

ax.set_xlim(-1, len(data_window))
ax.set_xticks(np.linspace(0, len(data_window) - 1, 10, dtype=int))
ax.set_xticklabels([t.strftime('%H:%M:%S') for t in data_window['bucket'][::len(data_window)//10]], rotation=45)
ax.set_ylabel("Price")
ax.set_xlabel("Time (3s Buckets)")
ax.set_title("Buy/Sell Volume Bubble Chart Over Time")
green_patch = mpatches.Patch(color='green', label='Buy Volume (Market + Pending)')
red_patch = mpatches.Patch(color='red', label='Sell Volume (Market + Pending)')
ax.legend(handles=[green_patch, red_patch])
ax.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)
