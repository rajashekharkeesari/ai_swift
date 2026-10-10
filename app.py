"""FastAPI backend for the SwiftVisa eligibility screening agent."""

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="SwiftVisa",
    description="AI-powered visa eligibility screening agent (RAG + Groq Llama 3.3)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScreenRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The applicant's visa query / profile")
    k: int = Field(3, ge=1, le=10, description="Number of documents to retrieve")


class RetrievedDoc(BaseModel):
    score: float
    country: str | None = None
    visa_type: str | None = None
    official_resource: str | None = None


class Telemetry(BaseModel):
    """Operational metrics tracked for every live API call."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    generation_latency_s: float
    pipeline_latency_s: float


class ScreenResponse(BaseModel):
    query: str
    response: str
    retrieved_documents: list[RetrievedDoc]
    telemetry: Telemetry


@app.get("/")
def home():
    return {"service": "SwiftVisa", "status": "ok", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/screen", response_model=ScreenResponse)
def screen(request: ScreenRequest):
    """Run the RAG pipeline for a visa eligibility query.

    For live API traffic we only track operational telemetry (tokens, cost,
    latency), the retrieved documents, and the generated answer via LangSmith.
    Quality metrics (retrieval / generation / LLM-judge) are intentionally NOT
    computed here — those belong to the offline evaluation harness.
    """
    # Deferred import so the app can start before the vector store / models
    # are built, and so startup stays fast.
    from src.Metrics.langsmith_tracking import traced_pipeline

    try:
        result = traced_pipeline(request.query, k=request.k)
    except Exception as exc:  # noqa: BLE001 - surface a clean API error
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    documents = [
        RetrievedDoc(
            score=float(score),
            country=doc.metadata.get("country"),
            visa_type=doc.metadata.get("visa_type"),
            official_resource=doc.metadata.get("official_resource"),
        )
        for score, doc in result["reranked_docs"]
    ]

    return ScreenResponse(
        query=request.query,
        response=result["answer"],
        retrieved_documents=documents,
        telemetry=Telemetry(**result["telemetry"]),
    )
