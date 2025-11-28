"""
Run advanced analytical queries and display results
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from sqlalchemy import text
import pandas as pd

def run_query(query_name, query_sql, limit=None):
    """Run a single query and display results"""
    print("\n" + "=" * 80)
    print(f"📊 {query_name}")
    print("=" * 80)
    
    try:
        with db.get_engine().connect() as conn:
            # Use text() wrapper for raw SQL
            result = conn.execute(text(query_sql))
            
            # Fetch results
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            if limit and len(df) > limit:
                print(f"Showing first {limit} of {len(df)} results:\n")
                print(df.head(limit).to_string(index=False))
            else:
                print(df.to_string(index=False))
            
            print(f"\n✅ Query executed successfully! ({len(df)} rows returned)")
            
    except Exception as e:
        print(f"❌ Error executing query: {e}")

def main():
    """Run all analytics queries"""
    
    print("\n" + "=" * 80)
    print("🚀 SMART BI PLATFORM - ADVANCED ANALYTICS")
    print("=" * 80)
    
    queries = {
        "1. Employee Salary Analysis with Percentiles": """
            WITH salary_stats AS (
    SELECT 
        e.emp_id,
        e.first_name || ' ' || e.last_name as employee_name,
        e.position,
        d.dept_name,
        e.salary,
        NTILE(4) OVER (ORDER BY e.salary) as salary_quartile,
        PERCENT_RANK() OVER (ORDER BY e.salary) as salary_percentile,
        AVG(e.salary) OVER () as company_avg_salary,
        AVG(e.salary) OVER (PARTITION BY d.dept_id) as dept_avg_salary
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
    -- Cast salary_percentile * 100 to numeric before ROUND
    ROUND((salary_percentile * 100)::numeric, 2)::text || '%' as percentile_rank,
    TO_CHAR(company_avg_salary, '$999,999.99') as company_avg,
    TO_CHAR(dept_avg_salary, '$999,999.99') as dept_avg
FROM salary_stats
ORDER BY salary DESC
LIMIT 15;

        """,
        
        "2. Monthly Sales Trend with Moving Averages": """
            WITH monthly_sales AS (
                SELECT 
                    DATE_TRUNC('month', sale_date) as month,
                    COUNT(*) as transaction_count,
                    SUM(total_amount) as revenue
                FROM sales
                WHERE status = 'completed'
                GROUP BY DATE_TRUNC('month', sale_date)
            )
            SELECT 
                TO_CHAR(month, 'YYYY-MM') as month,
                transaction_count,
                TO_CHAR(revenue, '$999,999,999.99') as revenue,
                TO_CHAR(LAG(revenue, 1) OVER (ORDER BY month), '$999,999,999.99') as prev_month,
                ROUND(
                    ((revenue - LAG(revenue, 1) OVER (ORDER BY month)) / 
                    NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0)) * 100, 2
                ) || '%' as growth_rate,
                TO_CHAR(
                    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
                    '$999,999,999.99'
                ) as three_month_avg
            FROM monthly_sales
            ORDER BY month DESC
            LIMIT 12
        """,
        
        "3. Customer RFM Segments (Top Spenders)": """
            WITH customer_metrics AS (
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name as customer_name,
                    CURRENT_DATE - MAX(s.sale_date) as recency_days,
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
                    NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,
                    NTILE(5) OVER (ORDER BY frequency) as f_score,
                    NTILE(5) OVER (ORDER BY monetary_value) as m_score
                FROM customer_metrics
            )
            SELECT 
                customer_name,
                recency_days,
                frequency,
                TO_CHAR(monetary_value, '$999,999.99') as lifetime_value,
                r_score, 
                f_score, 
                m_score,
                CASE 
                    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
                    WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
                    WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
                    WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                    WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
                    ELSE 'Potential'
                END as segment
            FROM rfm_scores
            ORDER BY monetary_value DESC
            LIMIT 20
        """,
        
        "4. Top 20 Products by Revenue": """
            WITH product_sales AS (
                SELECT 
                    p.product_id,
                    p.product_name,
                    p.category,
                    COUNT(s.sale_id) as times_sold,
                    SUM(s.quantity) as total_quantity,
                    SUM(s.total_amount) as revenue
                FROM products p
                LEFT JOIN sales s ON p.product_id = s.product_id AND s.status = 'completed'
                GROUP BY p.product_id, p.product_name, p.category
                HAVING SUM(s.total_amount) > 0
            )
            SELECT 
                product_name,
                category,
                times_sold,
                total_quantity,
                TO_CHAR(revenue, '$999,999.99') as revenue,
                DENSE_RANK() OVER (ORDER BY revenue DESC) as rank,
                ROUND((revenue / SUM(revenue) OVER ()) * 100, 2) || '%' as revenue_share
            FROM product_sales
            ORDER BY revenue DESC
            LIMIT 20
        """,
        
        "5. Sales Performance by Region": """
            SELECT 
                region,
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled,
                TO_CHAR(
                    SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END), 
                    '$999,999,999.99'
                ) as total_revenue,
                ROUND(
                    COUNT(CASE WHEN status = 'completed' THEN 1 END)::NUMERIC / 
                    COUNT(*) * 100, 2
                ) || '%' as completion_rate
            FROM sales
            GROUP BY region
            ORDER BY SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) DESC
        """,
        
        "6. Top 15 Performing Employees": """
            WITH emp_performance AS (
                SELECT 
                    e.emp_id,
                    e.first_name || ' ' || e.last_name as employee_name,
                    e.position,
                    d.dept_name,
                    COUNT(s.sale_id) as total_sales,
                    SUM(s.total_amount) as total_revenue,
                    AVG(s.total_amount) as avg_sale_value,
                    COUNT(DISTINCT s.customer_id) as unique_customers
                FROM employees e
                JOIN departments d ON e.dept_id = d.dept_id
                LEFT JOIN sales s ON e.emp_id = s.emp_id AND s.status = 'completed'
                WHERE e.is_active = TRUE
                GROUP BY e.emp_id, employee_name, e.position, d.dept_name
                HAVING COUNT(s.sale_id) > 0
            )
            SELECT 
                ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank,
                employee_name,
                position,
                dept_name,
                total_sales,
                TO_CHAR(total_revenue, '$999,999,999.99') as revenue,
                TO_CHAR(avg_sale_value, '$999,999.99') as avg_sale,
                unique_customers
            FROM emp_performance
            ORDER BY total_revenue DESC
            LIMIT 15
        """,
        
        "7. Department Performance Comparison": """
            SELECT 
                d.dept_name,
                d.location,
                COUNT(DISTINCT e.emp_id) as employee_count,
                TO_CHAR(AVG(e.salary), '$999,999.99') as avg_salary,
                COUNT(s.sale_id) as total_sales,
                TO_CHAR(SUM(s.total_amount), '$999,999,999.99') as total_revenue,
                TO_CHAR(
                    SUM(s.total_amount) / NULLIF(COUNT(DISTINCT e.emp_id), 0),
                    '$999,999.99'
                ) as revenue_per_employee
            FROM departments d
            LEFT JOIN employees e ON d.dept_id = e.dept_id AND e.is_active = TRUE
            LEFT JOIN sales s ON e.emp_id = s.emp_id AND s.status = 'completed'
            GROUP BY d.dept_id, d.dept_name, d.location
            ORDER BY SUM(s.total_amount) DESC NULLS LAST
        """,
        
        "8. Product Category Analysis": """
            SELECT 
                p.category,
                COUNT(DISTINCT p.product_id) as product_count,
                COUNT(s.sale_id) as times_sold,
                SUM(s.quantity) as units_sold,
                TO_CHAR(SUM(s.total_amount), '$999,999,999.99') as total_revenue,
                TO_CHAR(AVG(s.total_amount), '$999,999.99') as avg_transaction,
                ROUND(
                    (SUM(s.total_amount) / 
                    (SELECT SUM(total_amount) FROM sales WHERE status = 'completed')) * 100,
                    2
                ) || '%' as revenue_share
            FROM products p
            LEFT JOIN sales s ON p.product_id = s.product_id AND s.status = 'completed'
            GROUP BY p.category
            ORDER BY SUM(s.total_amount) DESC NULLS LAST
        """
    }
    
    # Run each query
    for query_name, query_sql in queries.items():
        run_query(query_name, query_sql)
        user_input = input("\n👉 Press Enter for next query (or type 'skip' to finish): ")
        if user_input.lower() == 'skip':
            break
    
    print("\n" + "=" * 80)
    print("✅ All analytics queries completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
