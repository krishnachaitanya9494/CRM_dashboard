import pandas as pd
import streamlit as st
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA

def show(df):
    st.title("📊 Future Predictions")

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    revenue_time_series = df.groupby(df['InvoiceDate'].dt.to_period("M")).agg({'UnitPrice': 'sum'}).reset_index()
    revenue_time_series.rename(columns={'UnitPrice': 'Revenue'}, inplace=True)
    revenue_time_series['InvoiceDate'] = revenue_time_series['InvoiceDate'].astype(str) + '-01'
    revenue_time_series['InvoiceDate'] = pd.to_datetime(revenue_time_series['InvoiceDate'])

    best_order = (2, 1, 2)
    arima_model = ARIMA(revenue_time_series['Revenue'], order=best_order)
    fitted_arima = arima_model.fit()
    forecast = fitted_arima.forecast(steps=6)

    future_dates = pd.date_range(start=revenue_time_series['InvoiceDate'].iloc[-1], periods=7, freq='M')[1:]
    forecast_df = pd.DataFrame({'Date': future_dates, 'Predicted Revenue': forecast})
    forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])

    st.subheader("📈 Revenue Forecast")
    fig_forecast = px.line(revenue_time_series, x="InvoiceDate", y="Revenue", markers=True, 
                           title="Revenue Forecasting (ARIMA)", labels={"InvoiceDate": "Date", "Revenue": "Revenue ($)"})
    fig_forecast.add_scatter(x=forecast_df['Date'], y=forecast_df['Predicted Revenue'], 
                             mode='lines+markers', name="Forecasted Revenue (ARIMA)")
    st.plotly_chart(fig_forecast, use_container_width=True)

    st.subheader("📈 Projected Annual Revenue & Profit")
    projected_revenue = forecast_df['Predicted Revenue'].sum()
    profit_margin = 0.30
    projected_profit = projected_revenue * profit_margin

    col1, col2 = st.columns(2)
    col1.metric(label="Estimated Annual Revenue", value=f"${projected_revenue:,.2f}")
    col2.metric(label="Estimated Annual Profit", value=f"${projected_profit:,.2f}")

    st.subheader("📦 Top Demanding Product Categories")
    top_categories = df.groupby("Category")["Quantity"].sum().sort_values(ascending=False).head(5).reset_index()
    fig_top_products = px.bar(top_categories, x="Quantity", y="Category", orientation='h', text="Quantity",
                              title="🔥 Top Selling Product Categories",
                              labels={"Quantity": "Total Quantity Sold", "Category": "Product Category"},
                              color="Quantity", color_continuous_scale="blues")
    fig_top_products.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_top_products, use_container_width=True)

    st.subheader("🌍 Top Demanding Category Per Country")
    top_category_by_country = df.groupby(["Country", "Category"])["Quantity"].sum().reset_index()
    top_category_by_country = top_category_by_country.loc[top_category_by_country.groupby("Country")["Quantity"].idxmax()]
    fig_category_country = px.bar(top_category_by_country, x="Country", y="Quantity", color="Category", text="Category",
                                  title="Top Selling Category in Each Country",
                                  labels={"Quantity": "Total Quantity Sold", "Country": "Country"},
                                  barmode="group", color_discrete_sequence=px.colors.qualitative.Set1)
    fig_category_country.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_category_country, use_container_width=True)

    st.subheader("📊 Inventory Turnover Rate")
    inventory_turnover = df.groupby(["StockCode", "Description"]).agg({'Quantity': 'sum'}).reset_index()
    inventory_turnover['Turnover Rate'] = inventory_turnover['Quantity'] / inventory_turnover['Quantity'].max() * 5
    fig_inventory_turnover = px.bar(inventory_turnover.head(10), x="Description", y="Turnover Rate",
                                    title="Inventory Turnover Rate",
                                    labels={"Description": "Product Name", "Turnover Rate": "Turnover Rate"},
                                    text="Turnover Rate", color="Turnover Rate",
                                    color_continuous_scale="viridis")
    fig_inventory_turnover.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig_inventory_turnover, use_container_width=True)

    st.subheader("🎯 Customer Lifetime Value (CLV) Forecast")
    customer_lifetime_value = df.groupby("CustomerID").agg({
        "InvoiceDate": "max",
        "InvoiceNo": "count",
        "UnitPrice": "sum"
    }).reset_index()
    customer_lifetime_value.rename(columns={"InvoiceNo": "Frequency", "UnitPrice": "Monetary"}, inplace=True)

    clv_best_order = (2, 1, 2)
    clv_arima_model = ARIMA(customer_lifetime_value['Monetary'], order=clv_best_order)
    fitted_clv_arima = clv_arima_model.fit()
    clv_forecast = fitted_clv_arima.forecast(steps=6)

    clv_dates = pd.date_range(start=pd.to_datetime("today"), periods=6, freq='M')
    clv_forecast_df = pd.DataFrame({'Date': clv_dates, 'Predicted CLV': clv_forecast})

    fig_clv_forecast = px.line(clv_forecast_df, x="Date", y="Predicted CLV", markers=True,
                               title="Customer Lifetime Value (CLV) Forecast (ARIMA)",
                               labels={"Date": "Month", "Predicted CLV": "Projected CLV ($)"})
    st.plotly_chart(fig_clv_forecast, use_container_width=True)
