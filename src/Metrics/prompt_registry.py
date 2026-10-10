"""Prompt versioning via the LangSmith prompt hub.

Push the SwiftVisa prompt to LangSmith (each push creates a new commit),
pull a specific version by commit hash, and list the version history.

Usage:
    python -m src.Metrics.prompt_registry push      # push current prompt
    python -m src.Metrics.prompt_registry list      # list versions
    python -m src.Metrics.prompt_registry pull      # pull latest

Requires LANGSMITH_API_KEY in the environment.
"""

import sys

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langsmith import Client

from src.prompt import PROMPT

load_dotenv()

PROMPT_NAME = "swiftvisa-eligibility"


def _client():
    return Client()


def push_prompt(prompt_name=PROMPT_NAME):
    """Push the current PROMPT template to LangSmith as a new version.

    Returns the URL of the pushed prompt commit.
    """
    template = PromptTemplate.from_template(PROMPT)
    url = _client().push_prompt(prompt_name, object=template)
    return url


def pull_prompt(prompt_name=PROMPT_NAME, commit=None):
    """Pull a prompt from LangSmith.

    Args:
        prompt_name: Registered prompt name.
        commit: Optional commit hash. If omitted, pulls the latest version.
            Use the form "name:commit" semantics handled here automatically.
    """
    identifier = f"{prompt_name}:{commit}" if commit else prompt_name
    return _client().pull_prompt(identifier)


def list_versions(prompt_name=PROMPT_NAME, limit=20):
    """Return a list of (commit_hash, created_at) for the prompt's versions."""
    commits = []
    for commit in _client().list_prompt_commits(prompt_name, limit=limit):
        commits.append(
            {
                "commit_hash": getattr(commit, "commit_hash", None),
                "created_at": str(getattr(commit, "created_at", "")),
            }
        )
    return commits


def _main(argv):
    action = argv[0] if argv else "list"

    if action == "push":
        url = push_prompt()
        print(f"Pushed '{PROMPT_NAME}'. View it at:\n{url}")
    elif action == "pull":
        commit = argv[1] if len(argv) > 1 else None
        pulled = pull_prompt(commit=commit)
        label = commit or "latest"
        print(f"Pulled '{PROMPT_NAME}' ({label}):\n{pulled}")
    elif action == "list":
        versions = list_versions()
        if not versions:
            print(f"No versions found for '{PROMPT_NAME}'. Push one first.")
        for i, v in enumerate(versions, 1):
            print(f"{i:>2}. {v['commit_hash']}  {v['created_at']}")
    else:
        print(__doc__)


if __name__ == "__main__":
    _main(sys.argv[1:])
