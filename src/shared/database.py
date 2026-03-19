'''
Database Service Module.
This module handles the connection to Azure PostgreSQL
It uses SQLAlchemy to define the tables and insert the data safely
'''
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from src.shared.config import settings

Base = declarative_base()

# Define the table schema
class FinancialReport(Base):
    __tablename__ = "reports_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Define Database Manager class
class DatabaseService:
    def __init__(self):
        # 🛑 TEMPORARY BYPASS: Ignore Pydantic and use the string directly!
        db_url = "postgresql://username:password@crew-ai-as3485.postgres.database.azure.com:5432/postgres?sslmode=require"
        
        # Clean the string
        db_url = db_url.strip().strip('"').strip("'")
        
        # Fix the postgres:// prefix if necessary
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        print(f"🚀 Attempting to connect to DB... (Scheme: {db_url.split('://')[0]})")

        # Create engine and tables
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def save_report(self, ticker: str, content: str):
        """Saves a generated financial report to the database."""
        session = self.SessionLocal()
        try:
            new_report = FinancialReport(ticker=ticker, content=content)
            session.add(new_report)
            session.commit()
            print(f"✅ Saved {ticker} report to Database (ID: {new_report.id})")
        except Exception as e:
            print(f"❌ Database Error: {e}")
            session.rollback()
            raise e
        finally:
            session.close()