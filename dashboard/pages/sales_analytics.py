"""
Sales Analytics Page
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import api


def render():
    st.header("💰 Sales Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        months = st.slider("Months to show", 6, 24, 12)
    with col2:
        top_n = st.slider("Top N products", 10, 30, 15)
    
    # Monthly Trends
    sales_data = api.get("/analytics/sales/monthly", {"months": months})
    if sales_data:
        df = pd.DataFrame(sales_data)
        df['revenue_num'] = df['revenue'].apply(api.parse_numeric)
        
        col1, col2 = st.columns(2)
        with col1:
            fig_line = px.line(df, x='month', y='revenue_num', 
                             title="Monthly Revenue Trend")
            st.plotly_chart(fig_line, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(df, x='month', y='revenue_num', 
                           title="Revenue by Month")
            st.plotly_chart(fig_bar, use_container_width=True)
