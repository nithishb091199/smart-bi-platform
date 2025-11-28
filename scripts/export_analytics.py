"""
Export analytics results to CSV files
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from sqlalchemy import text
import pandas as pd

def export_analytics():
    """Export key analytics to CSV files"""
    
    print("\n📁 Exporting Analytics to CSV Files...")
    print("=" * 60)
    
    # Create data folder if not exists
    os.makedirs('data', exist_ok=True)
    
    exports = {
        'department_performance.csv': "SELECT * FROM vw_department_performance ORDER BY total_sales DESC",
        'monthly_sales_trend.csv': "SELECT * FROM vw_monthly_sales_trend ORDER BY month DESC LIMIT 24",
        'top_employees.csv': "SELECT * FROM vw_top_employees LIMIT 50",
        'customer_lifetime_value.csv': """
            SELECT * FROM vw_customer_lifetime_value 
            WHERE lifetime_value > 0 
            ORDER BY lifetime_value DESC 
            LIMIT 100
        """,
        'product_performance.csv': """
            SELECT * FROM vw_product_performance 
            WHERE total_revenue > 0
            ORDER BY total_revenue DESC 
            LIMIT 100
        """
    }
    
    with db.get_engine().connect() as conn:
        for filename, query in exports.items():
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            df = pd.DataFrame(rows, columns=columns)
            filepath = os.path.join('data', filename)
            df.to_csv(filepath, index=False)
            print(f"  ✓ Exported {filename} ({len(df)} rows)")
    
    print("\n✅ All analytics exported successfully!")
    print(f"📂 Files saved in: {os.path.abspath('data')}")

if __name__ == "__main__":
    export_analytics()
