"""
Data Generation Script
Generates realistic business data for the BI platform
"""

import sys
import os
from datetime import datetime, timedelta
import random
from decimal import Decimal
from faker import Faker
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from sqlalchemy import text

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible data
random.seed(42)

class DataGenerator:
    """Generates synthetic business data"""
    
    def __init__(self):
        self.engine = db.get_engine()
        self.session = db.get_session()
        
        # Configuration
        self.num_departments = 8
        self.num_employees = 200
        self.num_products = 150
        self.num_customers = 1000
        self.num_sales = 5000
        
        # Store IDs for referencing
        self.dept_ids = []
        self.emp_ids = []
        self.product_ids = []
        self.customer_ids = []
        
        print("🚀 Data Generator Initialized")
        print(f"Target Records:")
        print(f"  - Departments: {self.num_departments}")
        print(f"  - Employees: {self.num_employees}")
        print(f"  - Products: {self.num_products}")
        print(f"  - Customers: {self.num_customers}")
        print(f"  - Sales: {self.num_sales}")
        print("=" * 60)
    
    def clear_all_data(self):
        """Clear existing data from all tables"""
        print("\n🗑️  Clearing existing data...")
        
        try:
            with self.engine.connect() as conn:
                # Disable triggers temporarily
                conn.execute(text("SET session_replication_role = 'replica';"))
                
                # Delete in reverse order of dependencies
                tables = [
                    'transactions', 'sales', 'customer_churn_predictions',
                    'sales_predictions', 'audit_log', 'customers',
                    'products', 'employees', 'departments'
                ]
                
                for table in tables:
                    conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
                    print(f"  ✓ Cleared {table}")
                
                # Re-enable triggers
                conn.execute(text("SET session_replication_role = 'origin';"))
                conn.commit()
                
            print("✅ All data cleared successfully!\n")
            
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            raise
    
    def generate_departments(self):
        """Generate department records"""
        print("📊 Generating Departments...")
        
        departments_data = [
            ('Sales', 'New York', 500000.00),
            ('Marketing', 'San Francisco', 350000.00),
            ('Engineering', 'Seattle', 800000.00),
            ('Human Resources', 'Chicago', 200000.00),
            ('Finance', 'New York', 400000.00),
            ('Operations', 'Dallas', 300000.00),
            ('Customer Service', 'Austin', 250000.00),
            ('Research & Development', 'Boston', 600000.00),
        ]
        
        try:
            with self.engine.connect() as conn:
                for dept_name, location, budget in departments_data:
                    result = conn.execute(text(
                        """
                        INSERT INTO departments (dept_name, location, budget)
                        VALUES (:name, :location, :budget)
                        RETURNING dept_id
                        """
                    ), {"name": dept_name, "location": location, "budget": budget})
                    
                    dept_id = result.scalar()
                    self.dept_ids.append(dept_id)
                
                conn.commit()
            
            print(f"  ✓ Created {len(self.dept_ids)} departments")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    def generate_employees(self):
        """Generate employee records"""
        print("👥 Generating Employees...")
        
        positions = {
            1: ['Sales Manager', 'Sales Representative', 'Account Executive'],
            2: ['Marketing Manager', 'Content Writer', 'SEO Specialist', 'Social Media Manager'],
            3: ['Software Engineer', 'Senior Developer', 'DevOps Engineer', 'QA Engineer', 'Tech Lead'],
            4: ['HR Manager', 'Recruiter', 'HR Coordinator'],
            5: ['Finance Manager', 'Accountant', 'Financial Analyst'],
            6: ['Operations Manager', 'Supply Chain Analyst', 'Logistics Coordinator'],
            7: ['Customer Service Manager', 'Support Agent', 'Service Representative'],
            8: ['Research Scientist', 'Data Scientist', 'Product Manager']
        }
        
        try:
            # First, create managers (no manager_id)
            managers = []
            for dept_id in self.dept_ids:
                first_name = fake.first_name()
                last_name = fake.last_name()
                emp_code = f"EMP{dept_id:03d}001"
                email = f"{first_name.lower()}.{last_name.lower()}@company.com"
                position = positions[dept_id][0]  # First position is manager
                salary = round(random.uniform(80000, 150000), 2)
                join_date = fake.date_between(start_date='-8y', end_date='-2y')
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(
                        """
                        INSERT INTO employees 
                        (emp_code, first_name, last_name, email, phone, dept_id, 
                         position, salary, manager_id, join_date, is_active)
                        VALUES (:code, :fname, :lname, :email, :phone, :dept, 
                                :pos, :salary, NULL, :join_date, TRUE)
                        RETURNING emp_id
                        """
                    ), {
                        "code": emp_code, "fname": first_name, "lname": last_name,
                        "email": email, "phone": fake.phone_number()[:20], "dept": dept_id,
                        "pos": position, "salary": salary, "join_date": join_date
                    })
                    
                    emp_id = result.scalar()
                    managers.append((emp_id, dept_id))
                    self.emp_ids.append(emp_id)
                    conn.commit()
            
            # Now create regular employees with manager references
            employees_per_dept = (self.num_employees - len(managers)) // len(self.dept_ids)
            
            for dept_id in self.dept_ids:
                manager_id = next(m[0] for m in managers if m[1] == dept_id)
                dept_positions = positions[dept_id][1:]  # Exclude manager position
                
                for i in range(employees_per_dept):
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    emp_code = f"EMP{dept_id:03d}{i+2:03d}"
                    email = f"{first_name.lower()}.{last_name.lower()}{i}@company.com"
                    position = random.choice(dept_positions)
                    salary = round(random.uniform(40000, 95000), 2)
                    join_date = fake.date_between(start_date='-5y', end_date='-1m')
                    is_active = random.choices([True, False], weights=[0.95, 0.05])[0]
                    
                    with self.engine.connect() as conn:
                        result = conn.execute(text(
                            """
                            INSERT INTO employees 
                            (emp_code, first_name, last_name, email, phone, dept_id, 
                             position, salary, manager_id, join_date, is_active)
                            VALUES (:code, :fname, :lname, :email, :phone, :dept, 
                                    :pos, :salary, :manager, :join_date, :active)
                            RETURNING emp_id
                            """
                        ), {
                            "code": emp_code, "fname": first_name, "lname": last_name,
                            "email": email, "phone": fake.phone_number()[:20], "dept": dept_id,
                            "pos": position, "salary": salary, "manager": manager_id,
                            "join_date": join_date, "active": is_active
                        })
                        
                        emp_id = result.scalar()
                        self.emp_ids.append(emp_id)
                        conn.commit()
            
            print(f"  ✓ Created {len(self.emp_ids)} employees")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    def generate_products(self):
        """Generate product records"""
        print("📦 Generating Products...")
        
        categories = {
            'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera', 'Smart Watch'],
            'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Dress', 'Sweater'],
            'Home & Kitchen': ['Coffee Maker', 'Blender', 'Toaster', 'Microwave', 'Vacuum Cleaner'],
            'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Biography', 'Sci-Fi'],
            'Sports': ['Yoga Mat', 'Dumbbell Set', 'Running Shoes', 'Tennis Racket', 'Basketball']
        }
        
        try:
            product_num = 1
            for category, subcategories in categories.items():
                for sub_category in subcategories:
                    for variant in range(random.randint(2, 5)):
                        product_code = f"PRD{product_num:05d}"
                        product_name = f"{sub_category} - {fake.color_name()} Edition"
                        cost_price = round(random.uniform(10, 500), 2)
                        selling_price = round(cost_price * random.uniform(1.3, 2.5), 2)
                        stock_qty = random.randint(0, 500)
                        reorder_level = random.randint(10, 50)
                        
                        with self.engine.connect() as conn:
                            result = conn.execute(text(
                                """
                                INSERT INTO products 
                                (product_code, product_name, category, sub_category, 
                                 cost_price, selling_price, stock_quantity, reorder_level)
                                VALUES (:code, :name, :cat, :subcat, :cost, :price, :stock, :reorder)
                                RETURNING product_id
                                """
                            ), {
                                "code": product_code, "name": product_name, "cat": category,
                                "subcat": sub_category, "cost": cost_price, "price": selling_price,
                                "stock": stock_qty, "reorder": reorder_level
                            })
                            
                            product_id = result.scalar()
                            self.product_ids.append(product_id)
                            conn.commit()
                        
                        product_num += 1
                        
                        if product_num > self.num_products:
                            break
                    if product_num > self.num_products:
                        break
                if product_num > self.num_products:
                    break
            
            print(f"  ✓ Created {len(self.product_ids)} products")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    def generate_customers(self):
        """Generate customer records"""
        print("👤 Generating Customers...")
        
        segments = ['Premium', 'Regular', 'Occasional']
        
        try:
            for i in range(self.num_customers):
                customer_code = f"CUST{i+1:06d}"
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}{i}@email.com"
                phone = fake.phone_number()[:20]
                address = fake.street_address()
                city = fake.city()
                state = fake.state()
                postal_code = fake.postcode()
                reg_date = fake.date_between(start_date='-3y', end_date='-1m')
                segment = random.choices(segments, weights=[0.2, 0.5, 0.3])[0]
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(
                        """
                        INSERT INTO customers 
                        (customer_code, first_name, last_name, email, phone, address,
                         city, state, postal_code, registration_date, customer_segment)
                        VALUES (:code, :fname, :lname, :email, :phone, :addr,
                                :city, :state, :postal, :reg_date, :segment)
                        RETURNING customer_id
                        """
                    ), {
                        "code": customer_code, "fname": first_name, "lname": last_name,
                        "email": email, "phone": phone, "addr": address, "city": city,
                        "state": state, "postal": postal_code, "reg_date": reg_date,
                        "segment": segment
                    })
                    
                    customer_id = result.scalar()
                    self.customer_ids.append(customer_id)
                    conn.commit()
                
                if (i + 1) % 200 == 0:
                    print(f"  ⏳ Progress: {i + 1}/{self.num_customers}")
            
            print(f"  ✓ Created {len(self.customer_ids)} customers")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    def generate_sales(self):
        """Generate sales transactions"""
        print("💰 Generating Sales...")
        
        regions = ['North', 'South', 'East', 'West', 'Central']
        payment_methods = ['Credit Card', 'Debit Card', 'Cash', 'PayPal', 'Bank Transfer']
        statuses = ['completed', 'pending', 'cancelled']
        
        try:
            for i in range(self.num_sales):
                sale_code = f"SALE{i+1:07d}"
                customer_id = random.choice(self.customer_ids)
                emp_id = random.choice(self.emp_ids)
                product_id = random.choice(self.product_ids)
                quantity = random.randint(1, 10)
                
                # Get product price
                with self.engine.connect() as conn:
                    result = conn.execute(text(
                        "SELECT selling_price FROM products WHERE product_id = :pid"
                    ), {"pid": product_id})
                    unit_price = float(result.scalar())  # Convert Decimal to float
                
                discount = random.choices([0, 5, 10, 15, 20], weights=[0.5, 0.2, 0.15, 0.1, 0.05])[0]
                tax = 8.0  # 8% tax
                
                # All calculations in float
                subtotal = unit_price * quantity
                discount_amount = subtotal * (discount / 100.0)
                taxable = subtotal - discount_amount
                tax_amount = taxable * (tax / 100.0)
                total = round(taxable + tax_amount, 2)
                
                sale_date = fake.date_between(start_date='-2y', end_date='today')
                region = random.choice(regions)
                payment_method = random.choice(payment_methods)
                status = random.choices(statuses, weights=[0.9, 0.07, 0.03])[0]
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(
                        """
                        INSERT INTO sales 
                        (sale_code, customer_id, emp_id, product_id, quantity, unit_price,
                         discount_percent, tax_percent, total_amount, sale_date, region,
                         payment_method, status)
                        VALUES (:code, :cust, :emp, :prod, :qty, :price, :disc, :tax,
                                :total, :date, :region, :payment, :status)
                        RETURNING sale_id
                        """
                    ), {
                        "code": sale_code, "cust": customer_id, "emp": emp_id,
                        "prod": product_id, "qty": quantity, "price": unit_price,
                        "disc": discount, "tax": tax, "total": total, "date": sale_date,
                        "region": region, "payment": payment_method, "status": status
                    })
                    
                    sale_id = result.scalar()
                    
                    # Create corresponding transaction
                    trans_code = f"TXN{i+1:07d}"
                    trans_date = datetime.combine(sale_date, datetime.now().time())
                    
                    conn.execute(text(
                        """
                        INSERT INTO transactions
                        (transaction_code, customer_id, sale_id, amount, transaction_date,
                         transaction_type, payment_status)
                        VALUES (:code, :cust, :sale, :amount, :date, :type, :status)
                        """
                    ), {
                        "code": trans_code, "cust": customer_id, "sale": sale_id,
                        "amount": total, "date": trans_date, "type": "sale",
                        "status": "completed" if status == "completed" else "pending"
                    })
                    
                    conn.commit()
                
                if (i + 1) % 1000 == 0:
                    print(f"  ⏳ Progress: {i + 1}/{self.num_sales}")
            
            print(f"  ✓ Created {self.num_sales} sales and transactions")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    def update_customer_last_purchase(self):
        """Update last purchase dates for customers"""
        print("🔄 Updating customer last purchase dates...")
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(
                    """
                    UPDATE customers c
                    SET last_purchase_date = (
                        SELECT MAX(s.sale_date)
                        FROM sales s
                        WHERE s.customer_id = c.customer_id
                    )
                    WHERE EXISTS (
                        SELECT 1 FROM sales s WHERE s.customer_id = c.customer_id
                    )
                    """
                ))
                conn.commit()
            
            print("  ✓ Customer purchase dates updated")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    def generate_summary(self):
        """Display summary statistics"""
        print("\n" + "=" * 60)
        print("📈 DATA GENERATION SUMMARY")
        print("=" * 60)
        
        try:
            with self.engine.connect() as conn:
                tables = [
                    'departments', 'employees', 'products', 
                    'customers', 'sales', 'transactions'
                ]
                
                for table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table.capitalize():.<30} {count:>6} records")
                
                # Total sales amount
                result = conn.execute(text("SELECT SUM(total_amount) FROM sales"))
                total_sales = result.scalar() or 0
                print(f"\n  Total Sales Revenue:............. ${float(total_sales):,.2f}")
                
                # Date range
                result = conn.execute(text("SELECT MIN(sale_date), MAX(sale_date) FROM sales"))
                min_date, max_date = result.fetchone()
                print(f"  Sales Date Range:................ {min_date} to {max_date}")
                
            print("=" * 60)
            print("✅ Data generation completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
    
    def run(self, clear_existing=True):
        """Run complete data generation process"""
        start_time = datetime.now()
        print("\n" + "=" * 60)
        print("🚀 STARTING DATA GENERATION PROCESS")
        print("=" * 60)
        print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        try:
            if clear_existing:
                self.clear_all_data()
            
            self.generate_departments()
            self.generate_employees()
            self.generate_products()
            self.generate_customers()
            self.generate_sales()
            self.update_customer_last_purchase()
            self.generate_summary()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n⏱️  Total Time: {duration:.2f} seconds")
            print("\n🎉 All data generated successfully! Ready for analysis.\n")
            
        except Exception as e:
            print(f"\n❌ Data generation failed: {e}")
            raise

def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("SMART BI PLATFORM - DATA GENERATOR")
    print("=" * 60)
    
    generator = DataGenerator()
    
    # Ask user confirmation
    response = input("\n⚠️  This will clear existing data. Continue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        generator.run(clear_existing=True)
    else:
        print("\n❌ Operation cancelled by user.")

if __name__ == "__main__":
    main()
