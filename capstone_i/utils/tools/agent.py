from openai import OpenAI
from ..logger_helper import get_logger
from .. import db_helper
from dotenv import find_dotenv, load_dotenv
import os

# Load environment variables
env_file = find_dotenv()
load_dotenv(env_file)

client = OpenAI()
logger = get_logger("agent")

MODEL = "gpt-3.5-turbo"

# Get database schema for the tool description
database_schema = db_helper.get_database_schema()

tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "Get an answer from the SQL database based on a query. IMPORTANT: Results are limited to 10 rows maximum.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {database_schema}
                                The query should be returned in plain text, not in JSON.
                                IMPORTANT: All queries are automatically limited to 10 results maximum.
                                When user asks for more than 10 items, inform them that results are limited to 10.
                                The SQL query MUST include LIMIT 10 or lower.
                                """,
                    }
                },
                "required": ["query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a GitHub issue for human support when technical issues occur automatically. DO NOT use this for user support requests - those are handled differently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the support ticket"
                    },
                    "body": {
                        "type": "string", 
                        "description": "Detailed description of the technical issue"
                    }
                },
                "required": ["title", "body"]
            }
        }
    }
]

# Remove all the execution code - this should only define tools and client
logger.info("Agent tools and client initialized")