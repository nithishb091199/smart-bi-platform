"""
Test analytical views and queries
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from sqlalchemy import text
import pandas as pd

def test_views():
    """Test all analytical views"""
    
    print("\n" + "=" * 70)
    print("🔍 TESTING ANALYTICAL VIEWS")
    print("=" * 70)
    
    views = {
        'Department Performance': 'SELECT * FROM vw_department_performance ORDER BY total_sales DESC',
        'Monthly Sales Trend': 'SELECT * FROM vw_monthly_sales_trend LIMIT 12',
        'Top Employees': 'SELECT * FROM vw_top_employees LIMIT 10',
        'Customer Lifetime Value': 'SELECT * FROM vw_customer_lifetime_value ORDER BY lifetime_value DESC LIMIT 10',
        'Product Performance': 'SELECT * FROM vw_product_performance ORDER BY total_revenue DESC LIMIT 10'
    }
    
    with db.get_engine().connect() as conn:
        for view_name, query in views.items():
            print(f"\n📊 {view_name}")
            print("-" * 70)
            
            df = pd.read_sql(query, conn)
            print(df.to_string(index=False))
            print()

if __name__ == "__main__":
    test_views()
