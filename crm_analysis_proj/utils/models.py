import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def kmeans_segmentation(df_rfm, clusters=4):
    """Performs K-Means clustering on RFM data."""
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(df_rfm[['Recency', 'Frequency', 'Monetary']])
    
    kmeans = KMeans(n_clusters=clusters, random_state=42, n_init=10)
    df_rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
    
    return df_rfm

def forecast_trend(data, column_name, steps=3):
    """Forecasts future revenue, customers, or orders using Exponential Smoothing."""
    if len(data) >= 6:  # At least 6 months required for seasonal modeling
        model = ExponentialSmoothing(data[column_name], trend='add', seasonal='add', seasonal_periods=3).fit()
    else:
        model = ExponentialSmoothing(data[column_name], trend='add').fit()  # No seasonality if data is insufficient
    
    return model.forecast(steps=steps)
