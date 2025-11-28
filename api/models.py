"""
Pydantic models for API responses
"""
from pydantic import BaseModel
from typing import List, Optional

class HealthCheck(BaseModel):
    status: str

class TableInfo(BaseModel):
    table_name: str

class EmployeeSummary(BaseModel):
    employee_name: str
    position: str
    dept_name: str
    salary: str
    salary_quartile: int
    percentile_rank: str

class SalesTrend(BaseModel):
    month: str
    transaction_count: int
    revenue: str
    growth_rate: Optional[str] = None

class CustomerRFM(BaseModel):
    customer_name: str
    recency_days: Optional[float]
    frequency: int
    lifetime_value: str
    r_score: int
    f_score: int
    m_score: int
    segment: str
