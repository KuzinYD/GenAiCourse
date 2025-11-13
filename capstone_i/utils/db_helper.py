from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv
from .logger_helper import get_logger
import os

env_file = find_dotenv()
load_dotenv(env_file)

logger = get_logger("db_helper")

DATABASE_URL = os.getenv('DATABASE_URL')

def ask_database(query):

    safe_query = f"SELECT * FROM ({query.rstrip(';')}) AS subquery LIMIT 10"

    db_conn = create_engine(DATABASE_URL)
    try:
        with db_conn.connect() as conn:
            logger.info("Executing SAFE query: %s", safe_query)
            #raise Exception("Testing LLM error handling")  # For testing error handling
            result = conn.execute(text(safe_query))
            results = result.fetchall()
            logger.info("Query results: %s", results)
            return results
    except Exception as e:
        logger.exception("SQL error while executing query")
        raise Exception(f"SQL error: {e}") from e