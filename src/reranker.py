"""Cross-encoder reranking of retrieved documents."""

import os

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
SAVE_PATH = os.path.join(PROJECT_ROOT, "models", "cross-encoder-ms-marco-MiniLM-L-6-v2")

_cross_encoder = None


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def download_crossencoder():
    """Download the cross-encoder model and cache it locally."""
    model = CrossEncoder(MODEL_NAME)
    model.save(SAVE_PATH)


def _get_cross_encoder():
    """Lazily load the cached cross-encoder (offline)."""
    global _cross_encoder
    if _cross_encoder is None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        _cross_encoder = CrossEncoder(SAVE_PATH, device="cpu")
    return _cross_encoder


def predict_reranker(query, retrieved_docs):
    """Return (score, document) pairs sorted by descending relevance."""
    model = _get_cross_encoder()
    pairs = [[query, doc.page_content] for doc in retrieved_docs]
    scores = sigmoid(model.predict(pairs))
    return sorted(
        zip(scores, retrieved_docs),
        key=lambda x: x[0],
        reverse=True,
    )
