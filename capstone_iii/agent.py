import os
from dotenv import load_dotenv
import requests
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")  

model = init_chat_model("gpt-4.1")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
faiss_index = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = faiss_index.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (
            f"Source: {doc.metadata.get('source', 'unknown')}, "
            f"Page: {doc.metadata.get('page', 'unknown')}\n"
            f"Content: {doc.page_content}"
        )
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

@tool()
def github_support_ticket(query: str, email: str = None):
    """File a GitHub support ticket with the user's query if the answer is not found.
       Requires user's email for follow-up.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("REPO")  # e.g., "username/repo"
    if not email:
        return "Please provide your email address to file a support ticket."
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "title": "Support Request: " + query[:50],
        "body": f"User query: {query}\n\nUser email: {email}\n\nFiled automatically by the agent."
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return "GitHub support ticket filed successfully."
    else:
        return f"Failed to file GitHub ticket: {response.text}"

tools = [
    retrieve_context,
    github_support_ticket
]

prompt = (
    "You have access to a tool that retrieves context from a knowledge base. "
    "Use the tool to help answer user queries. "
    "Only reply to the retrieved context. "
    "If you cannot find the answer in the context, tell that you don't know and use the GitHub support ticket tool"
    "If the user requests to file a support ticket, ask for their email address if it is not provided. "
    "Once the user provides their email, file the ticket and confirm."
)

agent = create_agent(model, tools, system_prompt=prompt)