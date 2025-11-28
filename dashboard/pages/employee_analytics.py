"""
Employee Analytics Page
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from utils import api


def render():
    st.header("👥 Employee Analytics")
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        limit = st.slider("Show top employees", 10, 50, 20)
    with col2:
        salary_threshold = st.slider("Min Salary ($)", 40000, 150000, 60000)
    
    # Salary Analysis Table
    st.subheader("💰 Salary Distribution & Percentiles")
    employees = api.get("/analytics/employees/salary", {"limit": limit})
    
    if employees:
        df = pd.DataFrame(employees)
        st.dataframe(df, use_container_width=True)
        
        # Salary Histogram
        df['salary_num'] = df['salary'].apply(lambda x: api.parse_numeric(x))
        fig = px.histogram(
            df, x='salary_num', nbins=20,
            title="Salary Distribution",
            labels={'salary_num': 'Salary ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Salary vs Department
        fig2 = px.box(
            df, x='dept_name', y='salary_num',
            title="Salary by Department",
            color='dept_name'
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)
