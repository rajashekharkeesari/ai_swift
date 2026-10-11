# 🛂 SwiftVisa — AI-Powered Visa Eligibility Screening Agent

SwiftVisa is a RAG (Retrieval-Augmented Generation) assistant that checks a user's profile against real visa policy data and returns an eligibility verdict with reasons, next steps, missing information, and citations.

It combines **FAISS** semantic search, **Cross-Encoder reranking**, and **Groq (Llama-3.3-70b)** for generation, and uses **LangSmith** for tracing and for offline and online evaluation.

---

## ✨ Features

- 🔍 **Semantic search**: FAISS vector store built with Hugging Face `all-MiniLM-L6-v2` embeddings
- 🏆 **Cross-Encoder reranking**: `ms-marco-MiniLM-L-6-v2` re-scores retrieved documents; scores are sigmoid-normalized and sorted
- 🤖 **LLM reasoning**: Groq `llama-3.3-70b-versatile` generates the eligibility analysis
- 📋 **Structured output**: eligibility status, reasons, next steps, missing information, and citations
- 📈 **LangSmith observability**: step-by-step traces plus offline evaluation and online monitoring
- 📝 **Query logging**: last 20 queries with timestamps saved to `logs/queries.json`
- ⚡ **FastAPI backend**: lightweight REST API served with Uvicorn
- 🔒 **Offline models**: embedding and reranker models are cached locally, so no model downloads are needed at runtime

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
Prompt Formatter (user input + top reranked document)
    │
    ▼
Groq LLM (llama-3.3-70b-versatile)
    │
    ▼
Eligibility Response + Citations + Next Steps
    │
    ├──► Query Logger (logs/queries.json)
    └──► LangSmith (traces, evaluation, monitoring)
```

---

## 🗂️ Project Structure

```
ai_swift/
├── app.py                      # FastAPI entry point
├── requirements.txt
├── .env.example                # Environment variable template
│
├── src/
│   ├── Dataloader.py           # Loads visa JSON and builds LangChain Documents
│   ├── Embeddings.py           # FAISS vector store creation and loading
│   ├── retriver.py             # VisaRetriever: similarity search over FAISS
│   ├── reranker.py             # Cross-Encoder reranking
│   ├── prompt.py               # SwiftVisa system prompt template
│   ├── prompt_formater.py      # Retrieval + reranking + prompt formatting
│   ├── llm_model.py            # Groq LLM setup
│   └── logging.py              # JSON query/response logger
│
├── Data/
│   ├── visaType.json           # Visa policy dataset (source of truth)
│   └── vectorestore/           # Saved FAISS index (auto-generated)
│
├── models/                     # Cached embedding and reranker models
├── logs/queries.json           # Auto-generated query logs (last 20 entries)
└── Frontend/Visa/              # React frontend (Login, Signup, Home)
```

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (only for the frontend)
- A [Groq API key](https://console.groq.com/)
- A [LangSmith API key](https://smith.langchain.com/) (optional, for tracing and evaluation)

### 1. Clone the repository

```bash
git clone https://github.com/rajashekharkeesari/ai_swift.git
cd ai_swift
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key_here

# LangSmith (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=swiftvisa
```

### 5. Download models (first time only)

```bash
python src/reranker.py
```

The `all-MiniLM-L6-v2` embedding model downloads automatically on first run and is cached in `models/`.

### 6. Build the vector store (first time only)

```bash
python src/Dataloader.py
```

This loads `Data/visaType.json`, formats each visa entry, and saves the FAISS index to `Data/vectorestore/`.

### 7. Run the backend

```bash
python app.py
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### 8. Run the frontend (optional)

```bash
cd Frontend/Visa
npm install
npm run dev
```

---

## 🔁 RAG Pipeline Details

| Step | File | What it does |
|------|------|--------------|
| 1. Data loading | `Dataloader.py` | Reads `visaType.json` and turns each entry into a LangChain `Document` with country, visa type, age range, education, language requirements, financial proof, work permissions, PR path, and official resources |
| 2. Embeddings | `Embeddings.py` | Embeds documents with `all-MiniLM-L6-v2` and stores them in FAISS |
| 3. Retrieval | `retriver.py` | `VisaRetriever` runs top-k similarity search for the user's query |
| 4. Reranking | `reranker.py` | Cross-Encoder scores query-document pairs; scores are sigmoid-normalized and sorted in descending order |
| 5. Prompting | `prompt_formater.py` | Combines the query and the top reranked document into the SwiftVisa prompt template |
| 6. Generation | `llm_model.py` | Groq `llama-3.3-70b-versatile` produces the structured eligibility response |
| 7. Logging | `logging.py` | Saves the query, response, and retrieved documents; keeps the last 20 entries |

---

## 📈 Observability & Evaluation with LangSmith

SwiftVisa uses [LangSmith](https://smith.langchain.com/) to see what happens inside each request and to measure answer quality.

**Tracing.** With `LANGCHAIN_TRACING_V2=true`, each request is recorded as a trace covering retrieval, reranking, prompt formatting, and the LLM call, including inputs, outputs, latency, and token usage.

**Offline evaluation.** Run the pipeline against a fixed set of test profiles and score the outputs before shipping changes. This helps catch regressions when you change the embedding model, reranker, prompt, or LLM.

**Online monitoring.** Live traces are tracked in the LangSmith project dashboard so you can watch latency, errors, and cost, and review real queries after deployment.

### Evaluators (offline)

Each test case is a user profile plus the expected eligibility verdict. Every case is run through the full pipeline and scored by these evaluators:

| Evaluator | Type | What it checks |
|-----------|------|----------------|
| **Verdict correctness** | Code-based | Does the predicted status (Eligible / Not Eligible / Partially Eligible) match the expected label? |
| **Retrieval relevance** | Code-based | Is the correct visa document in the top-k results before reranking, and at rank 1 after reranking? |
| **Faithfulness (groundedness)** | LLM-as-judge | Is every reason in the answer supported by the retrieved visa document, with no invented requirements? |
| **Completeness** | LLM-as-judge | Does the response list missing information and next steps when the profile is incomplete? |
| **Citation presence** | Code-based | Does the answer include the country, visa type, and official resource of the retrieved document? |
| **Format validity** | Code-based | Does the response contain all required sections (status, reason, next steps, missing information, citations)? |

### Metrics

| Metric | Stage | How it is measured |
|--------|-------|--------------------|
| Verdict accuracy | Offline | Share of test cases where the verdict matches the expected label |
| Hit rate @ k | Offline | Share of cases where the correct document appears in the top-k retrieved results |
| Top-1 accuracy after reranking | Offline | Share of cases where the correct document is ranked first by the Cross-Encoder |
| Faithfulness score | Offline | Average judge score for groundedness across test cases |
| Format validity rate | Offline and online | Share of responses containing every required section |
| Latency (p50 / p95) | Online | End-to-end and per-stage time taken from LangSmith traces |
| Token usage | Online | Input and output tokens per request, taken from traces |
| Error rate | Online | Share of requests that fail or time out |

### Running an evaluation

Compare the results of each run in the LangSmith **Experiments** view to see whether a change to the embedding model, reranker, prompt, or LLM improved or hurt quality.

<!-- Add your latest results here once you have run the evaluation, e.g. verdict accuracy, hit rate @ k, and p95 latency. Only list numbers you have measured. -->

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
|-------|------------|
| Backend | FastAPI, Uvicorn |
| LLM | Groq: Llama-3.3-70b-versatile |
| Embeddings | Hugging Face: all-MiniLM-L6-v2 |
| Vector store | FAISS (LangChain) |
| Reranker | Cross-Encoder: ms-marco-MiniLM-L-6-v2 |
| RAG framework | LangChain |
| Observability & evaluation | LangSmith |
| Frontend | React, React Router, Tailwind CSS |
| Logging | JSON file-based logger |
| Language | Python 3.12, JavaScript (JSX) |

---

## ⚠️ Disclaimer

SwiftVisa gives informational guidance based on the policy data in `Data/visaType.json`. It is not legal or immigration advice. Always confirm requirements on the official government website before applying.

---

## 📄 License

Released under the [MIT License](LICENSE).

## 👨‍💻 Author

**Rajashekhar Keesari**: [GitHub](https://github.com/rajashekharkeesari)
