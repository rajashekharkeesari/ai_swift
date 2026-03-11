import json
import os
from datetime import datetime

log_file = os.path.join(os.getcwd(), "logs", "queries.json")
os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)

def log_query(query, response, retrieved_docs):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response": response,
        "retrieved_documents": retrieved_docs,
    }

    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_data)
    logs = logs[-20:] 

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)