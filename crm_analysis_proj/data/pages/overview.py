import streamlit as st
import plotly.express as px
import pandas as pd

def show(df):
    st.title("📊 Overview - CRM Analysis")

    if df is None or df.empty:
        st.warning("⚠ No data available. Please upload a valid dataset.")
        return

    required_columns = ['CustomerID', 'UnitPrice', 'Quantity', 'InvoiceDate', 'Country']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"🚨 Missing columns: {missing_columns}. Please check the dataset.")
        return

    try:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    except Exception as e:
        st.error(f"Error converting InvoiceDate to datetime: {e}")
        return

    if 'Revenue' not in df.columns:
        df['Revenue'] = df['UnitPrice'] * df['Quantity']

    if 'Profit' not in df.columns:
        df['Profit'] = df['Revenue'] * 0.3

    total_revenue = df['Revenue'].sum()
    new_customers = df['CustomerID'].nunique()
    avg_order_value = df['Revenue'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("🧑‍💼 New Customers", f"{new_customers}")
    col3.metric("📦 Avg Order Value", f"${avg_order_value:.2f}")

    if 'Category' in df.columns:
        category_revenue = df.groupby('Category')['Revenue'].sum().reset_index()
        revenue_chart = px.bar(
            category_revenue, 
            x='Category', 
            y='Revenue', 
            title="Revenue by Category", 
            color_discrete_sequence=["#7ED321"]
        )
        st.plotly_chart(revenue_chart, use_container_width=True)
    else:
        st.warning("⚠ 'Category' column not found. Skipping Revenue by Category chart.")

    if 'Category' in df.columns:
        df['Month'] = df['InvoiceDate'].dt.strftime('%Y-%m')
        monthly_category_summary = df.groupby(['Month', 'Category']).agg({'Revenue': 'sum', 'Profit': 'sum'}).reset_index()

        if not monthly_category_summary.empty:
            fig_monthly_category = px.bar(
                monthly_category_summary, 
                x='Month', 
                y='Revenue', 
                color='Category', 
                title="📆 Monthly Revenue by Category", 
                labels={'Revenue': 'Amount ($)'},
                barmode='stack'
            )
            st.plotly_chart(fig_monthly_category, use_container_width=True)

            fig_monthly_profit = px.bar(
                monthly_category_summary, 
                x='Month', 
                y='Profit', 
                color='Category', 
                title="📆 Monthly Profit by Category", 
                labels={'Profit': 'Amount ($)'},
                barmode='stack'
            )
            st.plotly_chart(fig_monthly_profit, use_container_width=True)
        else:
            st.warning("⚠ No data available for Monthly Revenue & Profit by Category.")
    else:
        st.warning("⚠ 'Category' column not found. Skipping Monthly Revenue & Profit by Category.")

    country_summary = df.groupby('Country').agg({'Revenue': 'sum', 'Profit': 'sum'}).reset_index()

    if not country_summary.empty:
        fig_country = px.bar(
            country_summary, 
            x='Country', 
            y=['Revenue', 'Profit'], 
            title="🌍 Revenue & Profit by Country", 
            labels={'value': 'Amount ($)', 'variable': 'Metric'},
            barmode='group',  
            color_discrete_map={'Revenue': '#e74c3c', 'Profit': '#f1c40f'}
        )
        st.plotly_chart(fig_country, use_container_width=True)
    else:
        st.warning("⚠ No data available for Revenue & Profit by Country.")
