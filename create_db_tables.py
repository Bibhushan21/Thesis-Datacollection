import sys
from pathlib import Path
import logging

# Add the project's root directory to the Python path
# This allows us to import modules from the 'data' package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.database_config import engine, Base
from data.models import User, AnalysisSession, AgentResult, AnalysisTemplate, SystemLog, AgentPerformance, AgentRating, AgentRatingSummary

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_tables(reset=False):
    """
    Connects to the database and creates all tables.
    If reset is True, it first drops all existing tables.
    """
    if reset:
        logging.info("Reset flag detected. Dropping all existing tables...")
        try:
            Base.metadata.drop_all(bind=engine)
            logging.info("All tables dropped successfully.")
        except Exception as e:
            logging.error(f"An error occurred while dropping tables: {e}")
            return

    logging.info("Attempting to connect to the database and create tables...")
    try:
        # The `create_all` method checks for the existence of tables before creating them.
        # It will create tables for all models that inherit from the `Base` class.
        Base.metadata.create_all(bind=engine)
        logging.info("Successfully created all tables (or they already existed).")
        logging.info("Database is ready for experiments.")
    except Exception as e:
        logging.error(f"An error occurred while creating the database tables: {e}")
        logging.error("Please check your database connection details in 'data/database_config.py' and ensure the PostgreSQL server is running.")

if __name__ == "__main__":
    should_reset = "--reset" in sys.argv
    create_tables(reset=should_reset)
