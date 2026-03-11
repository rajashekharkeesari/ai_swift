from langchain_community.vectorstores import FAISS
from src.Embeddings import embeddings
import os
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from src.reranker import predict_reranker

save_path = "./models/cross-encoder-ms-marco-MiniLM-L-6-v2"

vectorstore = FAISS.load_local(
    os.path.join(os.getcwd(), "Data", "vectorestore"),
    embeddings,
    allow_dangerous_deserialization=True
)


class VisaRetriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def similarity_search(self, query, k=3):
        return self.vectorstore.similarity_search(query, k=k)

    def format_results(self, docs, scores=None):
        output = []
        for i, doc in enumerate(docs, 1):
            entry = {
                "index": i,
                "country": doc.metadata.get("country", "N/A"),
                "visa_type": doc.metadata.get("visa_type", "N/A"),
                "official_resource": doc.metadata.get("official_resource", "N/A"),
                "content": doc.page_content.strip()
            }
            if scores:
                entry["score"] = round(float(scores[i - 1]), 4)
            output.append(entry)
        return output
    


visa_retriver_instance = VisaRetriever(vectorstore)

if __name__ == "__main__":
    retriverdemo = VisaRetriever(vectorstore)
    query = input("Enter your visa related query: ")
    docs = retriverdemo.similarity_search(query, k=3)

    print(f"\n{'='*50}")
    print("RETRIEVED DOCS (Before Reranking)")
    print(f"{'='*50}")

    for i, doc in enumerate(docs, 1):
        print(f"\nDOC {i}")
        print(f"Country   : {doc.metadata.get('country', 'N/A')}")
        print(f"Visa Type : {doc.metadata.get('visa_type', 'N/A')}")
        print(f"Resource  : {doc.metadata.get('official_resource', 'N/A')}")
        print(f"{'-'*50}")
        print(doc.page_content.strip()[:300])
        print(f"{'='*50}")

    print("\n Reranking with Cross Encoder...")
    ranked_docs = predict_reranker(query, docs)

    print(f"\n {'='*50}")
    print("RERANKED RESULTS (After Cross Encoder)")
    print(f"{'='*50}")

    for i, (score, doc) in enumerate(ranked_docs, 1):
        print(f"\nRANK {i} | Score: {score:.4f}")
        print(f"Country   : {doc.metadata.get('country', 'N/A')}")
        print(f"Visa Type : {doc.metadata.get('visa_type', 'N/A')}")
        print(f"Resource  : {doc.metadata.get('official_resource', 'N/A')}")
        print(f"{'-'*50}")
        print(doc.page_content.strip()[:300])
    print(ranked_docs[0][1].page_content)
