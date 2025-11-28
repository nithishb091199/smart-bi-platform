"""
🚀 Smart BI Platform - Interactive Dashboard
Built with Streamlit + FastAPI + PostgreSQL
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
sys.path.append("..")

from utils import api

# Page config
st.set_page_config(
    page_title="Smart BI Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Navigation")
page = st.sidebar.selectbox(
    "Choose Analytics Page:",
    ["📈 Dashboard Overview", "👥 Employee Analytics", "💰 Sales Analytics", 
     "👤 Customer RFM", "📦 Products & Departments"]
)

# Header
st.markdown('<h1 class="main-header">🧠 Smart Business Intelligence Platform</h1>', unsafe_allow_html=True)
st.markdown("**Real-time analytics powered by PostgreSQL + FastAPI + Streamlit**")

# Page routing
if page == "📈 Dashboard Overview":
    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        summary = api.get("/summary")
        if summary:
            depts = next((s['value'] for s in summary if s['metric'] == 'departments'), '0')
            st.metric("Departments", depts)
    
    with col2:
        if summary:
            emps = next((s['value'] for s in summary if s['metric'] == 'employees'), '0')
            st.metric("Employees", emps)
    
    with col3:
        if summary:
            sales = next((s['value'] for s in summary if s['metric'] == 'sales'), '0')
            st.metric("Total Sales", sales)
    
    with col4:
        if summary:
            revenue = next((s['value'] for s in summary if s['metric'] == 'total_revenue'), '$0')
            st.metric("Total Revenue", revenue)
    
    with col5:
        top_products = api.get("/analytics/products/top", {"limit": 1})
        if top_products:
            st.metric("Top Product Rank", f"#{top_products[0]['rank']}")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Products by Revenue")
        products = api.get("/analytics/products/top", {"limit": 10})
        if products:
            df = pd.DataFrame(products)
            df['revenue_num'] = df['revenue'].apply(api.parse_numeric)
            fig = px.bar(
                df, x='revenue_num', y='product_name', 
                orientation='h',
                title="Top Products",
                color='revenue_num',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Monthly Sales Trend")
        sales_trend = api.get("/analytics/sales/monthly", {"months": 12})
        if sales_trend:
            df = pd.DataFrame(sales_trend)
            df['revenue_num'] = df['revenue'].apply(api.parse_numeric)
            fig = px.line(
                df, x='month', y='revenue_num',
                title="Monthly Revenue Trend",
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

elif page == "👥 Employee Analytics":
    import pages.employee_analytics as emp_page
    emp_page.render()

elif page == "💰 Sales Analytics":
    import pages.sales_analytics as sales_page
    sales_page.render()

elif page == "👤 Customer RFM":
    import pages.customer_rfm as rfm_page
    rfm_page.render()

elif page == "📦 Products & Departments":
    import pages.products_departments as prod_page
    prod_page.render()


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Built with ❤️ using PostgreSQL + FastAPI + Streamlit<br>
        <a href='https://github.com/yourusername/smart-bi-platform'>Source Code</a>
    </div>
    """, 
    unsafe_allow_html=True
)
