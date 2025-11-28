"""
🚀 Smart Business Intelligence Platform API - CORRECTED VERSION
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import db
from api.utils import execute_query
from typing import List, Any

app = FastAPI(
    title="🧠 Smart BI Platform API",
    description="Advanced Business Intelligence API with ML-powered analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

@app.get("/")
async def root():
    return {
        "message": "🚀 Smart BI Platform API is running!",
        "endpoints": [
            "/health", "/tables", "/summary",
            "/analytics/employees/salary",
            "/analytics/sales/monthly",
            "/analytics/customers/rfm",
            "/analytics/products/top",
            "/analytics/departments"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy ✅", "database": "connected"}

@app.get("/tables")
async def list_tables(db_session: Session = Depends(get_db)):
    result = db_session.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    )
    tables = [row[0] for row in result.fetchall()]
    return {"tables": tables, "total": len(tables)}

@app.get("/summary")
async def database_summary(db_session: Session = Depends(get_db)):
    summary_query = """
    SELECT 'departments' as metric, COUNT(*)::text as value FROM departments
    UNION ALL 
    SELECT 'employees', COUNT(*)::text FROM employees
    UNION ALL 
    SELECT 'products', COUNT(*)::text FROM products
    UNION ALL 
    SELECT 'customers', COUNT(*)::text FROM customers
    UNION ALL 
    SELECT 'sales', COUNT(*)::text FROM sales
    UNION ALL 
    SELECT 'total_revenue', TO_CHAR(COALESCE(SUM(total_amount), 0), '$999,999,999.99') FROM sales
    ORDER BY metric
    """
    data = execute_query(db_session, summary_query)
    return {"summary": data}

@app.get("/analytics/employees/salary")
async def get_employee_salary_analysis(
    limit: int = Query(50, ge=1, le=200),
    db_session: Session = Depends(get_db)
):
    query = f"""
    WITH salary_stats AS (
        SELECT 
            e.first_name || ' ' || e.last_name as employee_name,
            e.position,
            d.dept_name,
            e.salary,
            NTILE(4) OVER (ORDER BY e.salary) as salary_quartile,
            PERCENT_RANK() OVER (ORDER BY e.salary) as salary_percentile
        FROM employees e
        JOIN departments d ON e.dept_id = d.dept_id
        WHERE e.is_active = TRUE
    )
    SELECT 
        employee_name,
        position,
        dept_name,
        TO_CHAR(salary, '$999,999.99') as salary,
        salary_quartile,
        ROUND(salary_percentile * 100, 2) || '%' as percentile_rank
    FROM salary_stats
    ORDER BY salary DESC
    LIMIT {limit}
    """
    data = execute_query(db_session, query)
    return {"employees": data}

@app.get("/analytics/sales/monthly")
async def get_monthly_sales_trend(
    months: int = Query(12, ge=1, le=36),
    db_session: Session = Depends(get_db)
):
    query = f"""
    WITH monthly_sales AS (
        SELECT 
            DATE_TRUNC('month', sale_date) as month,
            COUNT(*) as transaction_count,
            SUM(total_amount) as revenue
        FROM sales
        WHERE status = 'completed'
        GROUP BY DATE_TRUNC('month', sale_date)
        ORDER BY month DESC
        LIMIT {months}
    )
    SELECT 
        TO_CHAR(month, 'YYYY-MM') as month,
        transaction_count,
        TO_CHAR(revenue, '$999,999,999.99') as revenue,
        ROUND(
            ((revenue - LAG(revenue, 1) OVER (ORDER BY month DESC)) / 
            NULLIF(LAG(revenue, 1) OVER (ORDER BY month DESC), 0)) * 100, 2
        ) || '%' as growth_rate
    FROM monthly_sales
    ORDER BY month DESC
    """
    data = execute_query(db_session, query)
    return {"monthly_trends": data}

@app.get("/analytics/customers/rfm")
async def get_customer_rfm_analysis(
    limit: int = Query(50, ge=1, le=200),
    db_session: Session = Depends(get_db)
):
    query = f"""
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.first_name || ' ' || c.last_name as customer_name,
            COALESCE(CURRENT_DATE - MAX(s.sale_date), 999) as recency_days,
            COUNT(DISTINCT s.sale_id) as frequency,
            COALESCE(SUM(s.total_amount), 0) as monetary_value
        FROM customers c
        LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.status = 'completed'
        GROUP BY c.customer_id, customer_name
        HAVING COUNT(s.sale_id) > 0
    ),
    rfm_scores AS (
        SELECT 
            *,
            NTILE(5) OVER (ORDER BY recency_days ASC) as r_score,
            NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
            NTILE(5) OVER (ORDER BY monetary_value DESC) as m_score
        FROM customer_metrics
    )
    SELECT 
        customer_name,
        recency_days::integer,
        frequency,
        TO_CHAR(monetary_value, '$999,999.99') as lifetime_value,
        r_score, f_score, m_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '🏆 Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN '💎 Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN '✨ New'
            WHEN r_score <= 2 THEN '⚠️ At Risk'
            ELSE '🔄 Potential'
        END as segment
    FROM rfm_scores
    ORDER BY monetary_value DESC
    LIMIT {limit}
    """
    data = execute_query(db_session, query)
    return {"rfm_segments": data}

@app.get("/analytics/products/top")
async def get_top_products(
    limit: int = Query(20, ge=1, le=50),
    db_session: Session = Depends(get_db)
):
    query = f"""
    SELECT 
        p.product_name,
        p.category,
        COUNT(s.sale_id) as times_sold,
        SUM(s.quantity) as total_quantity,
        TO_CHAR(SUM(s.total_amount), '$999,999.99') as revenue,
        DENSE_RANK() OVER (ORDER BY SUM(s.total_amount) DESC) as rank
    FROM products p
    LEFT JOIN sales s ON p.product_id = s.product_id AND s.status = 'completed'
    GROUP BY p.product_id, p.product_name, p.category
    HAVING SUM(s.total_amount) > 0
    ORDER BY SUM(s.total_amount) DESC
    LIMIT {limit}
    """
    data = execute_query(db_session, query)
    return {"top_products": data}

@app.get("/analytics/departments")
async def get_department_performance(db_session: Session = Depends(get_db)):
    query = """
    SELECT 
        d.dept_name,
        d.location,
        COUNT(DISTINCT e.emp_id) as employee_count,
        TO_CHAR(AVG(e.salary), '$999,999.99') as avg_salary,
        COUNT(s.sale_id) as total_sales,
        TO_CHAR(COALESCE(SUM(s.total_amount), 0), '$999,999,999.99') as total_revenue,
        ROUND(
            COALESCE(SUM(s.total_amount), 0) / NULLIF(COUNT(DISTINCT e.emp_id), 0), 0
        ) as revenue_per_employee
    FROM departments d
    LEFT JOIN employees e ON d.dept_id = e.dept_id AND e.is_active = TRUE
    LEFT JOIN sales s ON e.emp_id = s.emp_id AND s.status = 'completed'
    GROUP BY d.dept_id, d.dept_name, d.location
    ORDER BY COALESCE(SUM(s.total_amount), 0) DESC NULLS LAST
    """
    data = execute_query(db_session, query)
    return {"departments": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
