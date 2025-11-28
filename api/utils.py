"""
API Utilities - Query execution and helpers
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

def execute_query(session: Session, query: str) -> List[Dict[str, Any]]:
    """Execute SQL query and return results as list of dictionaries"""
    try:
        result = session.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Query execution error: {e}")
        return []
