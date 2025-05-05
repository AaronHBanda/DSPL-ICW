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