from dotenv import load_dotenv, find_dotenv
from .logger_helper import get_logger
import os
import requests

env_file = find_dotenv()
load_dotenv(env_file)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")   # example: "yourusername/yourrepo"

logger = get_logger("github_helper")


def create_support_ticket(title: str, body: str):
    """
    Creates a GitHub issue using the GitHub REST API v3.
    """
    url = f"https://api.github.com/repos/{REPO}/issues"

    payload = {
        "title": title,
        "body": body
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        logger.info("Creating GitHub issue: %s", title)
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 201:
            logger.error("GitHub API error: %s", response.text)
            raise Exception(f"GitHub issue creation failed: {response.text}")

        data = response.json()
        logger.info("Issue created: %s", data.get("html_url"))
        return {"url": data.get("html_url")}

    except Exception as e:
        logger.exception("Error creating GitHub issue")
        raise Exception(f"SUPPORT_TICKET_ERROR: {e}") from e
