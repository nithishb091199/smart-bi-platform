"""
Customer RFM Analysis Page
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import api


def render():
    st.header("👤 Customer RFM Analysis")
    
    limit = st.slider("Show top customers", 20, 100, 50)
    
    rfm_data = api.get("/analytics/customers/rfm", {"limit": limit})
    
    if rfm_data:
        df = pd.DataFrame(rfm_data)
        df['lifetime_num'] = df['lifetime_value'].apply(api.parse_numeric)
        
        # RFM Score Matrix
        st.subheader("🎯 RFM Score Distribution")
        fig_scatter = px.scatter(
            df, x='frequency', y='lifetime_num',
            size='recency_days', color='segment',
            hover_name='customer_name',
            title="RFM Matrix: Frequency vs Lifetime Value"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Segment Breakdown
        st.subheader("📊 Customer Segments")
        segment_counts = df['segment'].value_counts()
        fig_pie = px.pie(values=segment_counts.values, names=segment_counts.index,
                        title="Customer Segments Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.dataframe(df[['customer_name', 'segment', 'recency_days', 'frequency', 'lifetime_value']], 
                    use_container_width=True)
