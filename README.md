# 🛂 SwiftVisa — AI-Powered Visa Eligibility Screening Agent

SwiftVisa is an intelligent RAG (Retrieval-Augmented Generation) based visa eligibility assistant. It analyzes a user's profile against real visa policy documents and determines eligibility with detailed explanations, next steps, and citations — powered by **Groq (Llama 3.3)**, **FAISS**, and **Cross-Encoder Reranking**.

---

## 🧠 How It Works

```
User Query
    │
    ▼
FAISS Vector Store (similarity search)
    │
    ▼
Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)
    │
    ▼
Prompt Formatter (user input + top reranked doc)
    │
    ▼
Groq LLM (Llama-3.3-70b-versatile)
    │
    ▼
Eligibility Response + Citations + Next Steps
    │
    ▼
Query Logger (logs/queries.json)
```

---

## ✨ Features

- 🔍 **Semantic Search** — FAISS vector store with HuggingFace `all-MiniLM-L6-v2` embeddings
- 🏆 **Cross-Encoder Reranking** — `ms-marco-MiniLM-L-6-v2` reranks retrieved docs for highest relevance
- 🤖 **LLM Reasoning** — Groq's `llama-3.3-70b-versatile` for fast, accurate eligibility analysis
- 📋 **Structured Output** — Eligibility status, reasons, next steps, missing info, and citations
- 📝 **Query Logging** — Logs last 20 queries with timestamps to `logs/queries.json`
- 🌐 **React Frontend** — Login, Signup, and Home pages built with React + Tailwind CSS
- ⚡ **FastAPI Backend** — Lightweight REST API served with Uvicorn
- 🔒 **Offline Models** — Embedding and reranker models run fully locally (no internet needed at runtime)

---

## 🗂️ Project Structure

```
ai_swift/
│
├── app.py                        # FastAPI entry point
│
├── src/
│   ├── __init__.py
│   ├── Dataloader.py             # Loads & formats visa JSON data into LangChain Documents
│   ├── Embeddings.py             # FAISS vector store creation & loading (HuggingFace embeddings)
│   ├── retriver.py               # VisaRetriever class — similarity search over FAISS
│   ├── reranker.py               # Cross-Encoder reranking with ms-marco-MiniLM-L-6-v2
│   ├── prompt.py                 # SwiftVisa system prompt template
│   ├── prompt_formater.py        # Combines retrieval + reranking + prompt formatting
│   ├── llm_model.py              # Groq LLM (Llama-3.3-70b-versatile) setup
│   └── logging.py                # JSON-based query/response logger
│
├── Data/
│   ├── visaType.json             # Visa policy dataset (source of truth)
│   └── vectorestore/            # Saved FAISS index (auto-generated)
│
├── models/
│   ├── sentence-transformers/    # Cached HuggingFace embedding model
│   └── cross-encoder-ms-marco-MiniLM-L-6-v2/   # Cached reranker model
│
├── logs/
│   └── queries.json             # Auto-generated query logs (last 20 entries)
│
└── frontend/
    ├── Home.jsx                 # Home page component
    ├── Login.jsx                # Login form (email, phone, password)
    └── Signup.jsx               # Signup form (email, phone, password)
```

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- [Groq API Key](https://console.groq.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/rajashekharkeesari/ai_swift.git
cd ai_swift
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Download Models (first time only)

```bash
# Download and cache the cross-encoder reranker model
python src/reranker.py
```

The HuggingFace embedding model (`all-MiniLM-L6-v2`) is downloaded automatically on first run and cached in the `models/` folder.

### 6. Build the Vector Store (first time only)

```bash
python src/Dataloader.py
```

This loads `Data/visaType.json`, formats each visa entry, and saves the FAISS index to `Data/vectorestore/`.

### 7. Run the Backend

```bash
python app.py
```

API available at `http://127.0.0.1:8000`  
Swagger docs at `http://127.0.0.1:8000/docs`

### 8. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔁 RAG Pipeline Details

### Step 1 — Data Loading (`Dataloader.py`)
Reads `visaType.json` and formats each visa entry into structured `LangChain Document` objects with fields including country, visa type, age range, education, language requirements, financial proof, work permissions, PR path, and official resources.

### Step 2 — Embeddings & Vector Store (`Embeddings.py`)
Uses `sentence-transformers/all-MiniLM-L6-v2` (runs fully offline via cached models) to embed documents into FAISS for fast similarity search.

### Step 3 — Retrieval (`retriver.py`)
`VisaRetriever` performs top-k similarity search on the FAISS index based on the user's query.

### Step 4 — Reranking (`reranker.py`)
`CrossEncoder (ms-marco-MiniLM-L-6-v2)` reranks retrieved documents using query-document pair scoring. Scores are normalized with sigmoid and sorted in descending order for highest relevance.

### Step 5 — Prompt Formatting (`prompt_formater.py`)
Combines the user query and the top reranked document into the `SwiftVisa` prompt template using LangChain's `PromptTemplate`.

### Step 6 — LLM Response (`llm_model.py`)
Groq's `llama-3.3-70b-versatile` generates a structured eligibility response including status, reasons, next steps, missing information, and document citations.

### Step 7 — Logging (`logging.py`)
Every query, response, and retrieved documents are logged to `logs/queries.json`. Only the last 20 entries are retained.

---

## 📤 Example Output

```
Eligibility Status: Eligible

Reason:
The applicant meets the age requirement (22 years, within 18–35 range),
holds a bachelor's degree satisfying the education requirement, and has
a valid job offer with employer sponsorship.

Recommended Next Steps:
1. Obtain IELTS score of 6.0 or above
2. Gather financial proof (bank statements for last 6 months)
3. Apply via the official portal listed below

Missing Information:
- English proficiency test score not provided

Citations / Retrieved Documents:
- Country: Canada | Visa Type: Skilled Worker
  Official Resource: https://www.canada.ca/immigration
```

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn |
| LLM | Groq — Llama-3.3-70b-versatile |
| Embeddings | HuggingFace — all-MiniLM-L6-v2 |
| Vector Store | FAISS (LangChain) |
| Reranker | CrossEncoder — ms-marco-MiniLM-L-6-v2 |
| RAG Framework | LangChain |
| Frontend | React, React Router, Tailwind CSS |
| Logging | JSON file-based logger |
| Language | Python 3.12, JavaScript (JSX) |

---

## 📄 License

This project is open source. Feel free to use and modify it.

---

## 👨‍💻 Author

**Rajashekhar Keesari**  
[GitHub](https://github.com/rajashekharkeesari)
