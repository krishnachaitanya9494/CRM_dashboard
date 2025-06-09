import streamlit as st
import pandas as pd

# Import page modules from 'pages' folder
import pages.overview as overview
import pages.rfm_analysis as rfm_analysis
import pages.churn_prediction as churn_prediction
import pages.customer_segmentation as customer_segmentation
import pages.future_predictions as future_predictions

# Set page configuration
st.set_page_config(page_title="CRM Dashboard", layout="wide")

# Required columns for the dataset
REQUIRED_COLUMNS = ['CustomerID', 'InvoiceDate', 'Quantity', 'UnitPrice']

@st.cache_data
def load_data(uploaded_file):
    """Load and preprocess the uploaded dataset."""
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

        # Ensure required columns exist
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"🚨 Missing required columns: {', '.join(missing_cols)}.")
            return None

        # Convert InvoiceDate
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

        # Compute Revenue
        df['Revenue'] = df['UnitPrice'] * df['Quantity']

        st.success("✅ Data loaded successfully.")
        return df

    except Exception as e:
        st.error(f"🚨 Error loading data: {e}")
        return None

# Sidebar: File upload
st.sidebar.header("📂 Upload Your Dataset")
st.sidebar.markdown("""
**📌 Required Columns:**
- `CustomerID`
- `InvoiceDate`
- `Quantity`
- `UnitPrice`
""")

uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Load and preprocess the data
df = load_data(uploaded_file)

# Sidebar: Navigation
st.sidebar.header("📊 CRM Dashboard Pages")
page = st.sidebar.radio(
    "Choose a page:",
    [
        "Overview",
        "RFM Analysis",
        "Churn Prediction",
        "Customer Segmentation",
        "Future Predictions"
    ]
)

# Route to the selected page
if df is not None and not df.empty:
    if page == "Overview":
        overview.show(df)
    elif page == "RFM Analysis":
        rfm_analysis.show(df)
    elif page == "Churn Prediction":
        churn_prediction.show(df)
    elif page == "Customer Segmentation":
        customer_segmentation.show(df)
    elif page == "Future Predictions":
        future_predictions.show(df)
else:
    st.warning("⚠ Please upload a valid dataset to proceed.")
