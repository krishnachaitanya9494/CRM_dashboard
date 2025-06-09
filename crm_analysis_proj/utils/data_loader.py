import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("data/data.csv")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d-%m-%Y %H:%M", errors='coerce')
    df['Revenue'] = df['UnitPrice'] * df['Quantity']
    return df
