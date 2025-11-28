-- ============================================
-- SMART BUSINESS INTELLIGENCE PLATFORM SCHEMA
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- DEPARTMENTS TABLE
-- ============================================
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100),
    budget DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- EMPLOYEES TABLE
-- ============================================
CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    emp_code VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    dept_id INTEGER REFERENCES departments(dept_id),
    position VARCHAR(100),
    salary DECIMAL(12, 2),
    manager_id INTEGER REFERENCES employees(emp_id),
    join_date DATE NOT NULL,
    termination_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PRODUCTS TABLE
-- ============================================
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(20) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    sub_category VARCHAR(50),
    cost_price DECIMAL(10, 2),
    selling_price DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CUSTOMERS TABLE
-- ============================================
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    postal_code VARCHAR(20),
    registration_date DATE NOT NULL,
    last_purchase_date DATE,
    customer_segment VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SALES TABLE
-- ============================================
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_code VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    emp_id INTEGER REFERENCES employees(emp_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    tax_percent DECIMAL(5, 2) DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    sale_date DATE NOT NULL,
    region VARCHAR(50),
    payment_method VARCHAR(20),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TRANSACTIONS TABLE
-- ============================================
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_code VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    sale_id INTEGER REFERENCES sales(sale_id),
    amount DECIMAL(12, 2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    transaction_type VARCHAR(20),
    payment_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AUDIT LOG TABLE
-- ============================================
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ML PREDICTIONS TABLES
-- ============================================
CREATE TABLE sales_predictions (
    prediction_id SERIAL PRIMARY KEY,
    prediction_date DATE NOT NULL,
    predicted_sales DECIMAL(15, 2),
    confidence_interval_lower DECIMAL(15, 2),
    confidence_interval_upper DECIMAL(15, 2),
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_churn_predictions (
    prediction_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    churn_probability DECIMAL(5, 4),
    risk_level VARCHAR(20),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_employees_dept ON employees(dept_id);
CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_employees_active ON employees(is_active);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_employee ON sales(emp_id);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_region ON sales(region);
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_products_category ON products(category);

-- ============================================
-- TRIGGERS
-- ============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_employees_timestamp
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_departments_timestamp
    BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_products_timestamp
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_customers_timestamp
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Low stock alert trigger
CREATE OR REPLACE FUNCTION check_low_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.stock_quantity <= NEW.reorder_level THEN
        INSERT INTO audit_log (table_name, operation, record_id, new_values)
        VALUES ('products', 'LOW_STOCK', NEW.product_id, 
                jsonb_build_object('product_code', NEW.product_code, 
                                   'stock_quantity', NEW.stock_quantity));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER low_stock_alert
    AFTER UPDATE OF stock_quantity ON products
    FOR EACH ROW EXECUTE FUNCTION check_low_stock();

-- ============================================
-- ANALYTICAL VIEWS
-- ============================================

-- Department Performance
CREATE VIEW vw_department_performance AS
SELECT 
    d.dept_id,
    d.dept_name,
    d.location,
    COUNT(DISTINCT e.emp_id) as employee_count,
    COALESCE(AVG(e.salary), 0) as avg_salary,
    COALESCE(SUM(s.total_amount), 0) as total_sales,
    COUNT(DISTINCT s.sale_id) as total_transactions
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id AND e.is_active = TRUE
LEFT JOIN sales s ON e.emp_id = s.emp_id
GROUP BY d.dept_id, d.dept_name, d.location;

-- Monthly Sales Trend
CREATE VIEW vw_monthly_sales_trend AS
SELECT 
    DATE_TRUNC('month', sale_date) as month,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    SUM(quantity) as total_units_sold
FROM sales
GROUP BY DATE_TRUNC('month', sale_date)
ORDER BY month DESC;

-- Top Performing Employees
CREATE VIEW vw_top_employees AS
SELECT 
    e.emp_id,
    e.first_name || ' ' || e.last_name as employee_name,
    e.position,
    d.dept_name,
    COUNT(s.sale_id) as total_sales,
    COALESCE(SUM(s.total_amount), 0) as total_revenue
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
LEFT JOIN sales s ON e.emp_id = s.emp_id
WHERE e.is_active = TRUE
GROUP BY e.emp_id, employee_name, e.position, d.dept_name
ORDER BY total_revenue DESC;

-- Customer Lifetime Value
CREATE VIEW vw_customer_lifetime_value AS
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name as customer_name,
    c.customer_segment,
    c.city,
    c.state,
    COUNT(DISTINCT s.sale_id) as purchase_count,
    COALESCE(SUM(s.total_amount), 0) as lifetime_value,
    COALESCE(AVG(s.total_amount), 0) as avg_order_value,
    MAX(s.sale_date) as last_purchase_date,
    CASE 
        WHEN MAX(s.sale_date) IS NULL THEN NULL
        ELSE CURRENT_DATE - MAX(s.sale_date)
    END as days_since_last_purchase
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, customer_name, c.customer_segment, c.city, c.state;

-- Product Performance
CREATE VIEW vw_product_performance AS
SELECT 
    p.product_id,
    p.product_code,
    p.product_name,
    p.category,
    p.sub_category,
    p.stock_quantity,
    COUNT(s.sale_id) as times_sold,
    COALESCE(SUM(s.quantity), 0) as total_quantity_sold,
    COALESCE(SUM(s.total_amount), 0) as total_revenue,
    p.selling_price - p.cost_price as profit_per_unit
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_code, p.product_name, p.category, 
         p.sub_category, p.stock_quantity, p.selling_price, p.cost_price
ORDER BY total_revenue DESC;
