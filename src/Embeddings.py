"""HuggingFace embeddings and FAISS vector store management."""

import os
import warnings

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

os.environ.setdefault("HF_HUB_OFFLINE", "1")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_PATH = os.path.join(PROJECT_ROOT, "Data", "vectorestore")
CACHE_FOLDER = os.path.join(PROJECT_ROOT, "models")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=CACHE_FOLDER,
    model_kwargs={
        "device": "cpu",
        "local_files_only": True,
    },
)


def create_vector_store(documents):
    """Create a FAISS vector store from documents, or load it if it already exists."""
    index_file = os.path.join(VECTOR_PATH, "index.faiss")

    if os.path.exists(index_file):
        return FAISS.load_local(
            VECTOR_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(VECTOR_PATH)
    return vectorstore
