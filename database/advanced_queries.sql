-- ============================================
-- ADVANCED SQL QUERIES FOR BI PLATFORM
-- Showcases: CTEs, Window Functions, Complex JOINs
-- ============================================

-- ============================================
-- 1. EMPLOYEE SALARY ANALYSIS WITH PERCENTILES
-- ============================================
-- Shows: Window functions, NTILE, salary distribution
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
        AVG(e.salary) OVER (PARTITION BY d.dept_id) as dept_avg_salary,
        e.salary - AVG(e.salary) OVER (PARTITION BY d.dept_id) as diff_from_dept_avg
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
    ROUND(salary_percentile * 100, 2) || '%' as percentile_rank,
    TO_CHAR(company_avg_salary, '$999,999.99') as company_avg,
    TO_CHAR(dept_avg_salary, '$999,999.99') as dept_avg,
    TO_CHAR(diff_from_dept_avg, '$999,999.99') as diff_from_dept_avg
FROM salary_stats
ORDER BY salary DESC;


-- ============================================
-- 2. MONTHLY SALES TREND WITH MOVING AVERAGES
-- ============================================
-- Shows: Date functions, LAG/LEAD, moving averages
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', sale_date) as month,
        COUNT(*) as transaction_count,
        SUM(total_amount) as revenue,
        AVG(total_amount) as avg_transaction
    FROM sales
    WHERE status = 'completed'
    GROUP BY DATE_TRUNC('month', sale_date)
)
SELECT 
    TO_CHAR(month, 'YYYY-MM') as month,
    transaction_count,
    TO_CHAR(revenue, '$999,999,999.99') as revenue,
    TO_CHAR(avg_transaction, '$999.99') as avg_transaction,
    TO_CHAR(LAG(revenue, 1) OVER (ORDER BY month), '$999,999,999.99') as prev_month_revenue,
    ROUND(
        ((revenue - LAG(revenue, 1) OVER (ORDER BY month)) / 
        NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0)) * 100, 2
    ) || '%' as month_over_month_growth,
    TO_CHAR(
        AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
        '$999,999,999.99'
    ) as three_month_moving_avg
FROM monthly_sales
ORDER BY month DESC;


-- ============================================
-- 3. CUSTOMER RFM ANALYSIS (Recency, Frequency, Monetary)
-- ============================================
-- Shows: Complex calculations, multiple CTEs, scoring logic
WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name as customer_name,
        c.email,
        c.customer_segment,
        CURRENT_DATE - MAX(s.sale_date) as recency_days,
        COUNT(DISTINCT s.sale_id) as frequency,
        SUM(s.total_amount) as monetary_value
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.status = 'completed'
    GROUP BY c.customer_id, customer_name, c.email, c.customer_segment
),
rfm_scores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,
        NTILE(5) OVER (ORDER BY frequency) as f_score,
        NTILE(5) OVER (ORDER BY monetary_value) as m_score
    FROM customer_metrics
),
rfm_segments AS (
    SELECT 
        *,
        (r_score + f_score + m_score) as rfm_total,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Potential'
        END as rfm_segment
    FROM rfm_scores
)
SELECT 
    customer_name,
    email,
    customer_segment,
    recency_days,
    frequency,
    TO_CHAR(monetary_value, '$999,999.99') as lifetime_value,
    r_score,
    f_score,
    m_score,
    rfm_segment
FROM rfm_segments
ORDER BY rfm_total DESC, monetary_value DESC;


-- ============================================
-- 4. PRODUCT PERFORMANCE WITH RANKING
-- ============================================
-- Shows: Multiple window functions, DENSE_RANK, partitioning
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_code,
        p.product_name,
        p.category,
        p.sub_category,
        COUNT(s.sale_id) as times_sold,
        SUM(s.quantity) as total_quantity,
        SUM(s.total_amount) as total_revenue,
        AVG(s.total_amount) as avg_sale_value,
        (p.selling_price - p.cost_price) * SUM(s.quantity) as total_profit
    FROM products p
    LEFT JOIN sales s ON p.product_id = s.product_id AND s.status = 'completed'
    GROUP BY p.product_id, p.product_code, p.product_name, p.category, 
             p.sub_category, p.selling_price, p.cost_price
)
SELECT 
    product_name,
    category,
    sub_category,
    times_sold,
    total_quantity,
    TO_CHAR(total_revenue, '$999,999.99') as revenue,
    TO_CHAR(total_profit, '$999,999.99') as profit,
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) as overall_rank,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) as category_rank,
    ROUND(
        (total_revenue / SUM(total_revenue) OVER ()) * 100, 2
    ) || '%' as revenue_contribution
FROM product_sales
WHERE total_revenue > 0
ORDER BY total_revenue DESC
LIMIT 20;


-- ============================================
-- 5. EMPLOYEE PERFORMANCE LEADERBOARD
-- ============================================
-- Shows: Ranking, performance metrics, multiple aggregations
WITH employee_performance AS (
    SELECT 
        e.emp_id,
        e.first_name || ' ' || e.last_name as employee_name,
        e.position,
        d.dept_name,
        COUNT(DISTINCT s.sale_id) as total_sales,
        SUM(s.total_amount) as total_revenue,
        AVG(s.total_amount) as avg_deal_size,
        COUNT(DISTINCT s.customer_id) as unique_customers,
        SUM(s.total_amount) / NULLIF(COUNT(DISTINCT s.sale_id), 0) as revenue_per_sale
    FROM employees e
    JOIN departments d ON e.dept_id = d.dept_id
    LEFT JOIN sales s ON e.emp_id = s.emp_id AND s.status = 'completed'
    WHERE e.is_active = TRUE
    GROUP BY e.emp_id, employee_name, e.position, d.dept_name
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank,
    employee_name,
    position,
    dept_name,
    total_sales,
    TO_CHAR(total_revenue, '$999,999,999.99') as total_revenue,
    TO_CHAR(avg_deal_size, '$999,999.99') as avg_deal_size,
    unique_customers,
    TO_CHAR(revenue_per_sale, '$999,999.99') as revenue_per_sale
FROM employee_performance
WHERE total_sales > 0
ORDER BY total_revenue DESC
LIMIT 15;


-- ============================================
-- 6. COHORT ANALYSIS - CUSTOMER RETENTION
-- ============================================
-- Shows: Advanced date logic, cohort analysis, retention calculation
WITH first_purchase AS (
    SELECT 
        customer_id,
        MIN(DATE_TRUNC('month', sale_date)) as cohort_month
    FROM sales
    WHERE status = 'completed'
    GROUP BY customer_id
),
customer_activity AS (
    SELECT 
        fp.customer_id,
        fp.cohort_month,
        DATE_TRUNC('month', s.sale_date) as activity_month,
        EXTRACT(YEAR FROM AGE(DATE_TRUNC('month', s.sale_date), fp.cohort_month)) * 12 +
        EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', s.sale_date), fp.cohort_month)) as months_since_first
    FROM first_purchase fp
    JOIN sales s ON fp.customer_id = s.customer_id
    WHERE s.status = 'completed'
)
SELECT 
    TO_CHAR(cohort_month, 'YYYY-MM') as cohort,
    COUNT(DISTINCT CASE WHEN months_since_first = 0 THEN customer_id END) as month_0,
    COUNT(DISTINCT CASE WHEN months_since_first = 1 THEN customer_id END) as month_1,
    COUNT(DISTINCT CASE WHEN months_since_first = 2 THEN customer_id END) as month_2,
    COUNT(DISTINCT CASE WHEN months_since_first = 3 THEN customer_id END) as month_3,
    COUNT(DISTINCT CASE WHEN months_since_first = 6 THEN customer_id END) as month_6,
    ROUND(
        COUNT(DISTINCT CASE WHEN months_since_first = 3 THEN customer_id END)::NUMERIC /
        NULLIF(COUNT(DISTINCT CASE WHEN months_since_first = 0 THEN customer_id END), 0) * 100, 2
    ) || '%' as retention_3m
FROM customer_activity
GROUP BY cohort_month
ORDER BY cohort_month DESC
LIMIT 12;


-- ============================================
-- 7. SALES FUNNEL ANALYSIS BY REGION
-- ============================================
-- Shows: Pivoting, aggregations by multiple dimensions
SELECT 
    region,
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled,
    TO_CHAR(SUM(total_amount) FILTER (WHERE status = 'completed'), '$999,999,999.99') as revenue,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC / COUNT(*) * 100, 2
    ) || '%' as completion_rate,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'cancelled')::NUMERIC / COUNT(*) * 100, 2
    ) || '%' as cancellation_rate
FROM sales
GROUP BY region
ORDER BY SUM(total_amount) FILTER (WHERE status = 'completed') DESC;


-- ============================================
-- 8. RECURSIVE QUERY - EMPLOYEE HIERARCHY
-- ============================================
-- Shows: Recursive CTEs, organizational structure
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: Top-level managers
    SELECT 
        emp_id,
        first_name || ' ' || last_name as employee_name,
        position,
        manager_id,
        1 as level,
        first_name || ' ' || last_name as hierarchy_path
    FROM employees
    WHERE manager_id IS NULL AND is_active = TRUE
    
    UNION ALL
    
    -- Recursive case: Employees with managers
    SELECT 
        e.emp_id,
        e.first_name || ' ' || e.last_name,
        e.position,
        e.manager_id,
        eh.level + 1,
        eh.hierarchy_path || ' > ' || e.first_name || ' ' || e.last_name
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.emp_id
    WHERE e.is_active = TRUE
)
SELECT 
    REPEAT('  ', level - 1) || employee_name as org_structure,
    position,
    level as hierarchy_level,
    hierarchy_path
FROM employee_hierarchy
ORDER BY hierarchy_path;


-- ============================================
-- 9. CUSTOMER LIFETIME VALUE WITH PREDICTION
-- ============================================
-- Shows: Statistical functions, prediction logic
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name as customer_name,
        c.registration_date,
        COUNT(s.sale_id) as total_purchases,
        SUM(s.total_amount) as total_spent,
        AVG(s.total_amount) as avg_order_value,
        MAX(s.sale_date) as last_purchase,
        CURRENT_DATE - MAX(s.sale_date) as days_since_last,
        EXTRACT(DAYS FROM AGE(MAX(s.sale_date), MIN(s.sale_date))) as customer_lifespan_days,
        COUNT(s.sale_id)::NUMERIC / 
            NULLIF(EXTRACT(DAYS FROM AGE(MAX(s.sale_date), MIN(s.sale_date))), 0) * 365 
            as purchases_per_year
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.status = 'completed'
    GROUP BY c.customer_id, customer_name, c.registration_date
    HAVING COUNT(s.sale_id) > 0
)
SELECT 
    customer_name,
    total_purchases,
    TO_CHAR(total_spent, '$999,999.99') as total_spent,
    TO_CHAR(avg_order_value, '$999.99') as avg_order_value,
    days_since_last,
    ROUND(purchases_per_year, 2) as estimated_purchases_per_year,
    TO_CHAR(
        avg_order_value * purchases_per_year * 3,  -- 3-year projection
        '$999,999.99'
    ) as projected_3yr_value,
    CASE 
        WHEN days_since_last > 180 THEN 'High Churn Risk'
        WHEN days_since_last > 90 THEN 'Medium Churn Risk'
        WHEN days_since_last > 30 THEN 'Low Churn Risk'
        ELSE 'Active'
    END as churn_risk
FROM customer_stats
WHERE customer_lifespan_days > 0
ORDER BY total_spent DESC
LIMIT 20;


-- ============================================
-- 10. YEAR-OVER-YEAR COMPARISON
-- ============================================
-- Shows: Complex date handling, year comparisons
WITH yearly_metrics AS (
    SELECT 
        EXTRACT(YEAR FROM sale_date) as year,
        EXTRACT(MONTH FROM sale_date) as month,
        COUNT(*) as transactions,
        SUM(total_amount) as revenue,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM sales
    WHERE status = 'completed'
    GROUP BY EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date)
)
SELECT 
    TO_CHAR(TO_DATE(month::TEXT, 'MM'), 'Month') as month_name,
    MAX(CASE WHEN year = 2023 THEN TO_CHAR(revenue, '$999,999,999.99') END) as revenue_2023,
    MAX(CASE WHEN year = 2024 THEN TO_CHAR(revenue, '$999,999,999.99') END) as revenue_2024,
    MAX(CASE WHEN year = 2025 THEN TO_CHAR(revenue, '$999,999,999.99') END) as revenue_2025,
    MAX(CASE WHEN year = 2023 THEN transactions END) as transactions_2023,
    MAX(CASE WHEN year = 2024 THEN transactions END) as transactions_2024,
    MAX(CASE WHEN year = 2025 THEN transactions END) as transactions_2025
FROM yearly_metrics
GROUP BY month
ORDER BY month;
