"""
Dashboard API Client - Connects to FastAPI backend
"""
import os
import requests
import pandas as pd
from typing import Dict, List, Any
import streamlit as st

# API Base URL - reads from environment variable or defaults to localhost
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

class BIApiClient:
    """Client to interact with BI Platform API"""
    
    @staticmethod
    def get(endpoint: str, params: Dict = None) -> List[Dict]:
        """Make GET request to API"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract data from response wrapper
            if isinstance(data, dict):
                for key in data:
                    if isinstance(data[key], list):
                        return data[key]
            return data
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to API at {API_BASE_URL}")
            st.info("Make sure FastAPI is running!")
            return []
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return []
    
    @staticmethod
    def format_currency(value: str) -> str:
        """Format currency strings"""
        return value if value and value != 'None' else '$0.00'
    
    @staticmethod
    def parse_numeric(value: str) -> float:
        """Parse numeric values from formatted strings"""
        try:
            if isinstance(value, str) and value != 'None':
                return float(value.replace('$', '').replace(',', '').replace('%', ''))
            return 0.0
        except:
            return 0.0

# Global client instance
api = BIApiClient()
