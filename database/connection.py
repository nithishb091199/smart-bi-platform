"""
Database connection manager
Handles PostgreSQL connections using SQLAlchemy
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'business_intelligence')
DB_USER = os.getenv('DB_USER', 'bi_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'SecurePass2024!')

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class DatabaseConnection:
    """Manages database connections"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connect()
    
    def connect(self):
        """Create database engine and session"""
        try:
            self.engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            print(f"✅ Connected to database: {DB_NAME} at {DB_HOST}:{DB_PORT}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        return self.engine
    
    def get_session(self):
        """Get new database session"""
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                # Fixed: Use text() wrapper for raw SQL
                result = conn.execute(text("SELECT 1 as test"))
                value = result.scalar()
                print(f"✅ Database connection test successful! (Test value: {value})")
                return True
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False

# Global database instance
db = DatabaseConnection()

if __name__ == "__main__":
    print("Testing database connection...")
    success = db.test_connection()
    if success:
        print("\n🎉 Database is ready for Docker deployment!")
