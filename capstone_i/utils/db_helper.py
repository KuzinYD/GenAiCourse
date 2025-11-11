from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv
from .logger_helper import get_logger
import os

env_file = find_dotenv()
load_dotenv(env_file)

logger = get_logger("db_helper")

DATABASE_URL = os.getenv('DATABASE_URL')

def ask_database(query):
    # enforce limit by injecting/overriding LIMIT 10
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

def get_database_schema():
    db_conn = create_engine(DATABASE_URL)
    try:
        with db_conn.connect() as conn:
            result = conn.execute(text("""
                        SELECT
                            TABLE_NAME,
                            COLUMN_NAME,
                            COLUMN_TYPE,
                            IS_NULLABLE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = 'wine'
                        ORDER BY TABLE_NAME, ORDINAL_POSITION;
            """))
            logger.info("Fetching database schema")
            schema = result.fetchall()
            schema_str = ""
            current_table = ""
            for row in schema:
                table_name, column_name, column_type, is_nullable = row
                if table_name != current_table:
                    if current_table != "":
                        schema_str += "\n"
                    schema_str += f"Table: {table_name}\n"
                    current_table = table_name
                schema_str += f"  - {column_name}: {column_type} (nullable: {is_nullable})\n"
            logger.info("Database schema built (%d rows)", len(schema))
            return schema_str
    except Exception as e:
        logger.exception("Error retrieving database schema")
        raise RuntimeError(f"Error retrieving database schema: {e}")