import json
import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from ..logger_helper import get_logger
from ..db_helper import ask_database
from ..github_helper import create_support_ticket

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
    "from a SQL database. You can also create support tickets on GitHub for technical issues. "
    "Never modify data — do not use DELETE, INSERT, UPDATE, DROP, or ALTER. "
    "Only use SELECT statements when accessing the database. "
    "When providing the price, use EUR currency."
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
            "Create a GitHub issue for human support when a technical issue occurs automatically, "
            "or when the user explicitly asks to open a support ticket for a technical problem. "
            "If the user asks to create a support ticket, first ask for the title and details of the issue "
            "before calling this tool. Do not use this for normal Q&A or general help requests."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the support ticket"},
                "body": {"type": "string", "description": "Detailed description of the technical issue"},
            },
            "required": ["title", "body"],
        },
    },
]


def run_agent_conversation(messages):
    """Handles model responses, optional tool calls, and final text reply."""
    try:
        # First model pass (may include tool calls)
        response = client.responses.create(
            model=MODEL,
            tools=tools,
            input=messages,
        )

        tool_result = None

        # Check if the model called a tool
        for item in response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)

                if item.name == "ask_database":
                    tool_result = ask_database(args["query"])

                elif item.name == "create_support_ticket":
                    tool_result = create_support_ticket(args["title"], args["body"])

        if tool_result is not None:
            tool_message = {"role": "assistant", "content": str(tool_result)}
            messages_with_tool = messages + [tool_message]
        else:
            messages_with_tool = messages

        response_final = client.responses.create(
            model=MODEL,
            input=messages_with_tool,
            instructions=instructions,
        )

        return response_final.output_text.strip()

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return "⚠️ An error occurred while processing your request."
