import plotly.express as px

def revenue_chart(df):
    """Creates a revenue bar chart by category."""
    category_revenue = df.groupby('Category')['Revenue'].sum().reset_index()
    return px.bar(category_revenue, x='Category', y='Revenue', title="Revenue Overview", color_discrete_sequence=["#7ED321"])

def rfm_pie_chart(df_rfm):
    """Creates a pie chart for RFM segments."""
    rfm_segments = df_rfm['Recency'].value_counts().reset_index()
    rfm_segments.columns = ['Recency Segment', 'Count']
    return px.pie(rfm_segments, names='Recency Segment', values='Count', title="RFM Segments Distribution")

def churn_pie_chart(df):
    """Creates a churn distribution pie chart."""
    churn_data = df.groupby('CustomerID')['Days_Since_Last_Purchase'].max().reset_index()
    churn_data['Churn'] = churn_data['Days_Since_Last_Purchase'] > 90
    return px.pie(churn_data, names='Churn', title="Churn Distribution")
