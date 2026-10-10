"""Dataset versioning via LangSmith.

Create a LangSmith dataset from the local labeled eval set, add examples (each
upload creates a new dataset version), tag versions, list the version history,
and diff two versions.

Usage:
    python -m src.Metrics.dataset_registry create
    python -m src.Metrics.dataset_registry tag <version_or_tag> <new_tag>
    python -m src.Metrics.dataset_registry versions
    python -m src.Metrics.dataset_registry diff <tag_a> <tag_b>

Requires LANGSMITH_API_KEY in the environment.
"""

import json
import os
import sys

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVAL_QUERIES_PATH = os.path.join(PROJECT_ROOT, "Data", "eval_queries.json")

DATASET_NAME = "swiftvisa-eval"
DATASET_DESCRIPTION = "Labeled visa eligibility queries for RAG evaluation."


def _client():
    return Client()


def load_eval_queries(path=EVAL_QUERIES_PATH):
    """Load the local labeled eval set."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_or_update_dataset(dataset_name=DATASET_NAME):
    """Create the dataset if needed and upload the local examples.

    Uploading examples creates a new dataset version in LangSmith.
    Returns the dataset id.
    """
    client = _client()

    if client.has_dataset(dataset_name=dataset_name):
        dataset = client.read_dataset(dataset_name=dataset_name)
    else:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=DATASET_DESCRIPTION,
        )

    rows = load_eval_queries()
    inputs = [{"query": r["query"]} for r in rows]
    outputs = [
        {
            "expected_country": r["expected_country"],
            "expected_visa_type": r["expected_visa_type"],
            "expected_keywords": r.get("expected_keywords", []),
        }
        for r in rows
    ]

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )
    return dataset.id


def tag_version(dataset_name=DATASET_NAME, as_of="latest", tag="prod"):
    """Attach a human-readable tag to a dataset version.

    Args:
        as_of: An existing version tag or ISO timestamp to tag.
        tag: The new tag name (e.g. "v1", "prod").
    """
    _client().update_dataset_tag(
        dataset_name=dataset_name,
        as_of=as_of,
        tag=tag,
    )


def list_versions(dataset_name=DATASET_NAME, limit=20):
    """Return the dataset's version history as a list of dicts."""
    dataset = _client().read_dataset(dataset_name=dataset_name)
    versions = []
    for v in _client().list_dataset_versions(dataset_id=dataset.id, limit=limit):
        versions.append(
            {
                "as_of": str(getattr(v, "as_of", "")),
                "tags": list(getattr(v, "tags", []) or []),
            }
        )
    return versions


def diff_versions(dataset_name=DATASET_NAME, from_version="v1", to_version="latest"):
    """Diff two dataset versions (added / removed / modified example ids)."""
    dataset = _client().read_dataset(dataset_name=dataset_name)
    diff = _client().diff_dataset_versions(
        dataset_id=dataset.id,
        from_version=from_version,
        to_version=to_version,
    )
    return {
        "added": list(getattr(diff, "examples_added", []) or []),
        "removed": list(getattr(diff, "examples_removed", []) or []),
        "modified": list(getattr(diff, "examples_modified", []) or []),
    }


def _main(argv):
    action = argv[0] if argv else "versions"

    if action == "create":
        dataset_id = create_or_update_dataset()
        print(f"Dataset '{DATASET_NAME}' ready (id={dataset_id}). A new version was created.")
    elif action == "tag":
        as_of = argv[1] if len(argv) > 1 else "latest"
        tag = argv[2] if len(argv) > 2 else "prod"
        tag_version(as_of=as_of, tag=tag)
        print(f"Tagged version '{as_of}' as '{tag}'.")
    elif action == "versions":
        for i, v in enumerate(list_versions(), 1):
            print(f"{i:>2}. {v['as_of']}  tags={v['tags']}")
    elif action == "diff":
        a = argv[1] if len(argv) > 1 else "v1"
        b = argv[2] if len(argv) > 2 else "latest"
        print(json.dumps(diff_versions(from_version=a, to_version=b), indent=2))
    else:
        print(__doc__)


if __name__ == "__main__":
    _main(sys.argv[1:])
