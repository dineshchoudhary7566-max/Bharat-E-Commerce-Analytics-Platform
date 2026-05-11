import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Base directory setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Importing necessary analysis functions
from src.analysis import (calculate_kpis, get_monthly_sales, get_category_performance, 
                          get_top_products, calculate_rfm, get_daily_sales_performance)

# Page Configuration
st.set_page_config(page_title="Indian E-Comm Analytics 🇮🇳", layout="wide", page_icon="📈")

# --- CUSTOM CSS FOR UI ---
st.markdown("""
    <style>
    .main-header {
        font-size: 60px; font-weight: 800;
        background: -webkit-linear-gradient(#FF4B4B, #FF9900);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0px;
    }
    .sub-header {
        font-size: 24px; color: #555; text-align: center; margin-bottom: 40px;
    }
    .feature-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;
        border-bottom: 4px solid #FF4B4B; height: 100%; transition: 0.3s;
    }
    /* KPI Card Styling */
    .kpi-card {
        padding: 20px; border-radius: 10px; color: white; text-align: center;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px;
    }
    .stApp { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: UPLOAD ---
st.sidebar.title("Data Control Center 📂")
uploaded_file = st.sidebar.file_uploader("Step 1: Upload your Sales Data file", type=["csv", "xlsx", "xls", "json"])

# --- MAIN LOGIC ---
if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if file_ext == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_ext in ['xls', 'xlsx']:
        df = pd.read_excel(uploaded_file)
    elif file_ext == 'json':
        df = pd.read_json(uploaded_file)
        
    df.columns = [c.strip() for c in df.columns]
    
    if 'OrderDate' in df.columns:
        df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    st.sidebar.markdown("---")
    st.sidebar.title("Navigation 🧭")
    
    selected_page = st.sidebar.selectbox("Step 2: Select Analysis Page:", 
        ["Overview", "Charts & Visuals", "Category Analysis", "Regional Analysis", "Customer Segmentation", "Basket Analysis"])

    # Date Filter
    st.sidebar.subheader("📅 Filter by Date")
    min_date = df['OrderDate'].min().date()
    max_date = df['OrderDate'].max().date()
    selected_dates = st.sidebar.date_input("Select Range:", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        df = df[(df['OrderDate'].dt.date >= start_date) & (df['OrderDate'].dt.date <= end_date)]

    # --- PAGES ---
    if selected_page == "Overview":
        st.title("📊 Sales Trends & KPIs (India)")
        kpis = calculate_kpis(df)
        
        # Colourful KPI Boxes
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""<div class='kpi-card' style='background-color: #4E73DF;'>
                <p style='margin:0; font-size:16px;'>Total Revenue</p>
                <h2 style='margin:0; color:white;'>₹{kpis['total_revenue']:,.0f}</h2>
            </div>""", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""<div class='kpi-card' style='background-color: #1CC88A;'>
                <p style='margin:0; font-size:16px;'>Total Orders</p>
                <h2 style='margin:0; color:white;'>{kpis['total_orders']}</h2>
            </div>""", unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""<div class='kpi-card' style='background-color: #36B9CC;'>
                <p style='margin:0; font-size:16px;'>Total Customers</p>
                <h2 style='margin:0; color:white;'>{kpis['total_customers']}</h2>
            </div>""", unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""<div class='kpi-card' style='background-color: #F6C23E;'>
                <p style='margin:0; font-size:16px;'>Avg Basket Value</p>
                <h2 style='margin:0; color:white;'>₹{kpis['avg_order_value']:,.0f}</h2>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Recent Transactions")
        st.dataframe(df.head(10), use_container_width=True)

    elif selected_page == "Charts & Visuals":
        st.title("📈 Business Intelligence Charts")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Revenue by Category")
            cat_perf = get_category_performance(df)
            fig_pie = px.pie(cat_perf, values='TotalAmount', names='CategoryName', hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.subheader("Top 10 Selling Products")
            top_p = get_top_products(df, n=10)
            fig_bar = px.bar(top_p, x='TotalAmount', y='ProductName', orientation='h', color='TotalAmount', color_continuous_scale='Bluered_r')
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("---")
        st.subheader("Weekly Sales Performance")
        daily_df = get_daily_sales_performance(df)
        day_col = 'Day_Name' if 'Day_Name' in daily_df.columns else daily_df.columns[0]
        fig_line = px.line(daily_df, x=day_col, y='TotalAmount', markers=True, title="Daily Revenue Trend", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_line, use_container_width=True)

    elif selected_page == "Category Analysis":
        st.title("📦 Category Analysis")
        cat_perf = get_category_performance(df)
        st.table(cat_perf)

    elif selected_page == "Regional Analysis":
        st.title("🌍 City Sales Distribution")
        city_col = 'City' if 'City' in df.columns else 'ShipCity'
        if city_col in df.columns:
            city_sales = df.groupby(city_col)['TotalAmount'].sum().reset_index().sort_values(by='TotalAmount', ascending=False)
            fig_city = px.bar(city_sales.head(10), x='TotalAmount', y=city_col, orientation='h', color='TotalAmount')
            st.plotly_chart(fig_city, use_container_width=True)

    elif selected_page == "Basket Analysis":
        st.title("🛒 Market Basket Analysis")
        try:
            basket = df.groupby(['OrderID', 'ProductName'])['ProductName'].count().unstack().fillna(0)
            basket_model = basket.applymap(lambda x: 1 if x > 0 else 0)
            basket_corr = basket_model.corr()
            basket_corr.index.name, basket_corr.columns.name = 'Product_A', 'Product_B'
            pairs = basket_corr.unstack().reset_index()
            pairs.columns = ['Product_A', 'Product_B', 'Score']
            top_pairs = pairs[(pairs['Product_A'] != pairs['Product_B']) & (pairs['Score'] > 0)].sort_values(by='Score', ascending=False).head(15)
            st.dataframe(top_pairs, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

    elif selected_page == "Customer Segmentation":
        st.title("👥 Customer RFM Segments")
        rfm = calculate_rfm(df)
        st.plotly_chart(px.scatter(rfm, x="Recency", y="Frequency", color="Segment", size="Monetary"), use_container_width=True)

else:
    # --- HOME PAGE TITLE CHANGED ---
    st.markdown("<h1 class='main-header'>Bharat E-Commerce Analytics Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Transforming Indian Retail Data into Smarter Decisions 🚀</p>", unsafe_allow_html=True)
    st.write("##")
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("""<div class='feature-box'><h3>📈 Sales Analytics</h3><p>View monthly revenue and growth trends with a single click.</p></div>""", unsafe_allow_html=True)
    with f2: st.markdown("""<div class='feature-box'><h3>👥 Customer RFM</h3><p>Understand your VIP customers and identify churn risk segments.</p></div>""", unsafe_allow_html=True)
    with f3: st.markdown("""<div class='feature-box'><h3>🛒 Basket Patterns</h3><p>Discover which products are most frequently bought together.</p></div>""", unsafe_allow_html=True)
    st.write("###")
    c_i1, c_i2, c_i3 = st.columns([1.2, 1, 1.2]) 
    with c_i2: st.image("https://img.icons8.com/clouds/500/000000/shop.png", use_container_width=True)
    st.write("##")
    st.info("👈 **Getting Started:** Upload your Sales Data (CSV, Excel, or JSON) from the sidebar to unlock the full dashboard!")
