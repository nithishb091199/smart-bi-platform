"""
Products & Departments Analytics
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import api


def render():
    st.header("📦 Products & 📋 Departments")
    
    tab1, tab2 = st.tabs(["🏆 Top Products", "🏢 Department Performance"])
    
    with tab1:
        limit = st.slider("Top products", 10, 50, 20)
        products = api.get("/analytics/products/top", {"limit": limit})
        
        if products:
            df = pd.DataFrame(products)
            df['revenue_num'] = df['revenue'].apply(api.parse_numeric)
            
            fig = px.treemap(
                df, path=['category', 'product_name'],
                values='revenue_num',
                color='revenue_num',
                title="Product Revenue by Category",
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        depts = api.get("/analytics/departments")
        if depts:
            df = pd.DataFrame(depts)
            df['total_revenue_num'] = df['total_revenue'].apply(api.parse_numeric)
            
            fig = px.bar(
                df, x='dept_name', y='total_revenue_num',
                title="Department Revenue Performance",
                color='total_revenue_num'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True)
