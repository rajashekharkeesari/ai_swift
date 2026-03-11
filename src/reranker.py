from sentence_transformers import CrossEncoder
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()

model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
save_path = "./models/cross-encoder-ms-marco-MiniLM-L-6-v2"

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def load_crossencoder(model_name, save_path):
    print(f"Downloading model: {model_name} ...")
    model = CrossEncoder(model_name)
    model.save(save_path)
    print(f"Model saved to: {save_path}")


def predict_reranker(query, retrieved_docs):
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    cross_encoder_model = CrossEncoder(
        "./models/cross-encoder-ms-marco-MiniLM-L-6-v2",
        device="cpu"
    )

    pairs = [[query, doc.page_content] for doc in retrieved_docs]

    scores = cross_encoder_model.predict(pairs)
    normalized_scores = sigmoid(scores)
    




    ranked_docs = sorted(zip(normalized_scores, retrieved_docs), key=lambda x: x[0], reverse=True)

    return ranked_docs


if __name__ == "__main__":
    if not os.path.exists(save_path):
        load_crossencoder(model_name, save_path)
    else:
        print(f"Model already exists at: {save_path}")