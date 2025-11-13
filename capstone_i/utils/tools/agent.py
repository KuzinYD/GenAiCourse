import json
import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from capstone_i.utils.logger_helper import get_logger
from capstone_i.utils.db_helper import ask_database
from capstone_i.utils.github_helper import create_support_ticket

logger = get_logger("agent")
env_file = find_dotenv()
load_dotenv(env_file)

client = OpenAI()
MODEL = os.getenv("MODEL")

database_schema_string = """Table: Red Columns: Name, Country, Region, Winery, Rating, NumberOfRatings, Price, Year 
Table: Rose Columns: Name, Country, Region, Winery, Rating, NumberOfRatings, Price, Year 
Table: Sparkling Columns: Name, Country, Region, Winery, Rating, NumberOfRatings, Price, Year 
Table: Varieties Columns: C1 
Table: White Columns: Name, Country, Region, Winery, Rating, NumberOfRatings, Price, Year"""

instructions = (
    "You are an AI assistant that helps users by answering questions about wines "
    "from a SQL database. You can also create support tickets on GitHub for technical issues."
    "Never modify data — do not use DELETE, INSERT, UPDATE, DROP, or ALTER. "
    "Only use SELECT statements when accessing the database."
    "When providing the price use EUR currency."
)

tools = [
    {
        "type": "function",
        "name": "ask_database",
        "description": f"""
                    Execute a SQL query against the wine database and return results.
                    Only use SELECT statements to retrieve data.
                    SQL should be written using this database schema:
                    {database_schema_string}
                    Never perform operations that modify data (DELETE, INSERT, UPDATE, DROP, ALTER).
                    """,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A safe, read-only SQL SELECT query based on the user's question.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "create_support_ticket",
        "description": (
            "Create a GitHub issue for human support when technical issues occur automatically. "
            "DO NOT use this for user support requests - those are handled differently."
        ),
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
]

def run_agent_conversation(messages):
    """Handles responses, tool calls, and final assistant replies."""
    try:
        response = client.responses.create(
            model=MODEL,
            tools=tools,
            input=messages,
        )

        # Process function calls (tool use)
        for item in response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)

                if item.name == "ask_database":
                    result = ask_database(args["query"])
                    messages.append({"role": "assistant", "content": str(result)})

                elif item.name == "create_support_ticket":
                    result = create_support_ticket(args["title"], args["body"])
                    messages.append({"role": "assistant", "content": str(result)})

        # Final message
        response_final = client.responses.create(
            model=MODEL,
            input=messages,
            instructions=instructions,
        )

        final_text = response_final.output_text.strip()
        messages.append({"role": "assistant", "content": final_text})

        return final_text

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return "⚠️ An error occurred while processing your request."