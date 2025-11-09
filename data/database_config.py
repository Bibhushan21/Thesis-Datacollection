import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import psycopg2
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "Thesis_result"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgre321")
}

# Database URL for SQLAlchemy
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Handle postgres:// to postgresql:// conversion for compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db_session():
    """
    Get a database session.
    Use this function to get a session for database operations.
    """
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        logger.error(f"Database session error: {str(e)}")
        raise

def close_db_session(session):
    """
    Close a database session properly.
    """
    try:
        session.close()
    except Exception as e:
        logger.error(f"Error closing database session: {str(e)}")

@contextmanager
def get_db_connection():
    """
    Get a raw database connection using psycopg2.
    Use this function for raw SQL operations.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password']
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def get_db():
    """
    FastAPI dependency to get database session.
    Yields a database session that will be automatically closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """
    Test database connection.
    Returns True if successful, False otherwise.
    """
    try:
        session = get_db_session()
        # Simple query to test connection - using text() for SQLAlchemy 2.0
        session.execute(text("SELECT 1"))
        close_db_session(session)
        logger.info("Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False 