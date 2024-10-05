import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style='dark')

st.set_page_config(page_title="Bike Rental Analysis Dashboard", layout="wide")

@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/day_clean.csv")
    hour_df = pd.read_csv("dashboard/hour_clean.csv")
    return day_df, hour_df

day_df, hour_df = load_data()

date_time_columns = ['dteday']
day_df.sort_values(by='dteday', inplace=True)
day_df.reset_index(inplace=True)

for column in date_time_columns:
    day_df[column] = pd.to_datetime(day_df[column])


st.title("Bike Rental Analysis Dashboard")

def create_weathersit_allrent_df(df):
    weathersit_allrent_df = df.copy()
    weathersit_allrent_df = weathersit_allrent_df.reset_index()
    weathersit_allrent_df.rename(columns={
        "instant": "customer_count",
        "cnt": "total_rent"
    }, inplace=True)

    return weathersit_allrent_df

def create_sum_order_allrent_df(df):
    sum_order_allrent_df = df.groupby(['season', 'dteday']).cnt.sum().sort_values(ascending=False).reset_index()
    return sum_order_allrent_df

def create_sum_order_casualrent_df(df):
    sum_order_casualrent_df = df.groupby(['season', 'dteday']).casual.sum().sort_values(ascending=False).reset_index()
    return sum_order_casualrent_df


with st.sidebar:

    main_df = day_df

    years_select = st.selectbox(
        label = 'Select Years',
        options = ['All Years', '2011', '2012'],
        index = 0
    )

    weathersit_select = st.multiselect(
        label = 'Pick the Weather',
        options = ['springer', 'summer', 'fall', 'winter'],
        default = ['springer', 'summer', 'fall', 'winter']
    )

    if weathersit_select:
        main_df = main_df[(main_df['season'].isin(weathersit_select))]

    if years_select == 'All Years':

        weathersit_rent_df = create_weathersit_allrent_df(main_df)
        sum_order_allrent_df = create_sum_order_allrent_df(main_df)
        sum_order_casualrent_df = create_sum_order_casualrent_df(main_df)

    else:# elif years_select == '2011' or years_select == '2012':

        filtered_df = main_df[main_df['dteday'].dt.year == int(years_select)]
        weathersit_rent_df = create_weathersit_allrent_df(filtered_df)
        sum_order_allrent_df = create_sum_order_allrent_df(filtered_df)
        sum_order_casualrent_df = create_sum_order_casualrent_df(filtered_df)


col1, col2 = st.columns(2)

with col1:
    total_orders = weathersit_rent_df['total_rent'].nunique()
    st.metric("Total Orders", value=f'{total_orders:,}')

with col2:
    total_rent = weathersit_rent_df.total_rent.sum()
    st.metric("Total Rent", value=f'{total_rent:,}')

st.markdown("---")

st.header("Total Overall Bike Rentals by Month")
st.markdown("This chart below shows total bike rent over a year.")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(
    weathersit_rent_df['dteday'],
    weathersit_rent_df['total_rent'],
    linewidth=2,
    alpha=0.7,
    color='#418a1d'
)
ax.tick_params(axis='y', labelsize=10)
ax.tick_params(axis='x', labelsize=10)
plt.title('Monthly Bike Rental')
plt.ylabel('Rent Frequency')

st.pyplot(fig)

st.markdown("---")

st.header("Bike Rental by Season Condition")
st.markdown("This barplot below shows how season condition could affect renting behaviour.")


fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ['#80ff40', '#4083ff', '#ff5d40', '#D3D3D3']

sns.barplot(x='season', y='casual', data=sum_order_casualrent_df, palette=colors, ax=ax[0])
# ax[0].set_ylabel("")
ax[0].set_xlabel("Season", fontsize=30)
ax[0].set_title("Casual Bike Rentals by Season", loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='season', y='cnt', data=sum_order_allrent_df, palette=colors, ax=ax[1])
# ax[1].set_ylabel("Total Orders", fontsize=30)
ax[1].set_xlabel("Season", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Overall Bike Rentals by Season", loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)