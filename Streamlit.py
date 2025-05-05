# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Set page configuration 
st.set_page_config(page_title="Sri Lanka NDVI Dashboard", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("processed_lka_ndvi_data.csv")

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['NDVI Value'] = pd.to_numeric(df['NDVI Value'], errors='coerce')
    df['Long Term Average NDVI'] = pd.to_numeric(df['Long Term Average NDVI'], errors='coerce')
    df['NDVI Anomaly in Percentage (%)'] = pd.to_numeric(df['NDVI Anomaly in Percentage (%)'], errors='coerce')
    df['Number of Pixels'] = pd.to_numeric(df['Number of Pixels'], errors='coerce')

    df = df[(df['NDVI Value'] >= -1) & (df['NDVI Value'] <= 1)]
    return df

df = load_data()

# Title and Description 
st.markdown("""
    <h1 style='font-size: 60px; color: orange;'>Sri Lanka NDVI Dashboard (2002 - 2025)</h1>
    <p style='font-size: 17px; color: pink;'>
        Visualizing vegetation health across Sri Lanka using NDVI data from NASA MODIS satellites. <br><br>
    </p>
""", unsafe_allow_html=True)

# Sidebar filters
region_options = df['District'].unique()
selected_region = st.sidebar.selectbox("Select District", sorted(region_options))

# Horizontal date range slider
date_min = df['Date'].min().date()
date_max = df['Date'].max().date()
date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
    format="YYYY-MM"
)
# District filters
mask = (
    (df['District'] == selected_region) &
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1]))
)
filtered_df = df[mask]

# Summary metrics
st.subheader("NDVI Summary Statistics")

avg_ndvi = round(filtered_df['NDVI Value'].mean(), 3)
max_ndvi = round(filtered_df['NDVI Value'].max(), 3)
min_ndvi = round(filtered_df['NDVI Value'].min(), 3)

st.markdown("""
    <style>
    .metrics-row {
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }
    .metric-container {
        flex: 1;
        background-color: 	#343434;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .metric-label {
        font-weight: bold;
        color: #FFFFFF;
        font-size: 18px;
    }
    .metric-value {
        font-size: 35px;
        color: #0072B2;
    }
    .metric-delta-positive {
        font-size: 15px;
        color: green;
    }
    .metric-delta-negative {
        font-size: 14px;
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

def delta_html(value):
    if value >= 0:
        return f'<div class="metric-delta-positive">↑ {value:+.3f}</div>'
    else:
        return f'<div class="metric-delta-negative">↓ {value:+.3f}</div>'

st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-container">
            <div class="metric-label">Average NDVI</div>
            <div class="metric-value">{avg_ndvi}</div>
        </div>
        <div class="metric-container">
            <div class="metric-label">Max NDVI</div>
            <div class="metric-value">{max_ndvi}</div>
            {delta_html(max_ndvi - avg_ndvi)}
        </div>
        <div class="metric-container">
            <div class="metric-label">Min NDVI</div>
            <div class="metric-value">{min_ndvi}</div>
            {delta_html(min_ndvi - avg_ndvi)}
        </div>
    </div>
""", unsafe_allow_html=True)

# Display the dataset
st.subheader("Dataset Preview")
st.dataframe(df)

# Plot 1: NDVI over time
st.subheader("NDVI Trends Over Time")
fig1 = px.line(filtered_df, x='Date', y='NDVI Value', title='NDVI Over Time', labels={'NDVI Value': 'NDVI', 'Date': 'Date'})
st.plotly_chart(fig1, use_container_width=True)

# Plot 2: NDVI vs Long-Term Average 
st.subheader("NDVI vs Long-Term Average (LTA)")
fig2 = px.line(
    filtered_df,
    x='Date',
    y=['NDVI Value', 'Long Term Average NDVI'],
    title='NDVI vs Long-Term Average',
    labels={'value': 'NDVI', 'variable': 'NDVI Type', 'Date': 'Date'}
)

fig2.for_each_trace(
    lambda t: t.update(line=dict(color='light blue')) if t.name == 'NDVI Value' else t.update(line=dict(color='orange'))
)

st.plotly_chart(fig2, use_container_width=True)

# Plot 3: NDVI Anomaly (%)
st.subheader("NDVI Anomalies [%]")
fig3 = px.bar(filtered_df, x='Date', y='NDVI Anomaly in Percentage (%)', title='NDVI Anomaly (%) Over Time',
              labels={'NDVI Anomaly in Percentage (%)': 'NDVI Anomaly (%)', 'Date': 'Date'})
st.plotly_chart(fig3, use_container_width=True)

# Plot 4: Number of Pixels Used
st.subheader("Number of Pixels Used")
fig4 = px.line(
    filtered_df,
    x='Date',
    y='Number of Pixels',
    title='Number of Pixels Used (Data Coverage)',
    labels={'Number of Pixels': 'Pixels', 'Date': 'Date'}
)
fig4.update_traces(line=dict(color='red')) 
st.plotly_chart(fig4, use_container_width=True)

# Plot 5: Seasonal NDVI Averages
st.subheader("Seasonal NDVI Averages")
df['Month'] = df['Date'].dt.month
fig5 = px.bar(df, x='Month', y='NDVI Value', title='NDVI by Month Across Years',
              labels={'Month': 'Month', 'NDVI Value': 'NDVI'})
st.plotly_chart(fig5, use_container_width=True)


# Plot 6: NDVI Value vs Long Term Average NDVI
st.subheader("NDVI Value vs Long Term Average NDVI")
fig6 = px.scatter(
    filtered_df,
    x='NDVI Value',
    y='Long Term Average NDVI',
    title='NDVI Value vs Long Term Average NDVI',
    labels={'NDVI Value': 'NDVI Value', 'Long Term Average NDVI': 'Long Term Average NDVI'},
    opacity=0.6,
    trendline="ols"
)
st.plotly_chart(fig6, use_container_width=True)

# Setting background image
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("BG.jpg")


