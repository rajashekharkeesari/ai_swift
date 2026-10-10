"""FAISS-backed retriever for visa policy documents."""

import os
import warnings

from langchain_community.vectorstores import FAISS

from src.Embeddings import embeddings

warnings.filterwarnings("ignore", category=DeprecationWarning)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_PATH = os.path.join(PROJECT_ROOT, "Data", "vectorestore")

vectorstore = FAISS.load_local(
    VECTOR_PATH,
    embeddings,
    allow_dangerous_deserialization=True,
)


class VisaRetriever:
    """Thin wrapper around a FAISS vector store for similarity search."""

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def similarity_search(self, query, k=3):
        return self.vectorstore.similarity_search(query, k=k)


visa_retriver_instance = VisaRetriever(vectorstore)
