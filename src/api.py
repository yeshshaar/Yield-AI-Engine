import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from src.chains import run_evaluation_chain, stream_evaluation, AVAILABLE_MODELS, DEFAULT_MODEL
from src.vector_store import save_candidate_to_vector_db, search_similar_candidates
from src.database import init_db, save_evaluation, get_all_evaluations
from src.sanitizer import clean_pii
from src.jd_rag import index_jd, retrieve_relevant_jd_context
from src.ragas_evaluator import build_ragas_sample, evaluate_pipeline

# ─── App Init ────────────────────────────────────────────────────────────────
app = FastAPI(title="Yield-AI Advanced Engine", version="3.0")

# ✅ CORS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()
    print("✅ Database initialised.")

# ─── Global Error Handler (prevents HTML responses) ──────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

# ─── Request Models ──────────────────────────────────────────────────────────
class EvaluationRequest(BaseModel):
    candidate_name: str
    resume_text: str
    jd_text: str
    jd_id: str = "default"
    model_name: str = DEFAULT_MODEL

    @field_validator("resume_text", "jd_text", "candidate_name")
    @classmethod
    def must_not_be_empty(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} must not be empty.")
        return v.strip()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class RagasRequest(BaseModel):
    samples: list

class IndexJDRequest(BaseModel):
    jd_text: str
    jd_id: str

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {
        "status": "Yield-AI API v3.0 Online",
        "backends": list(AVAILABLE_MODELS.keys())
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/models")
def list_models():
    return {
        "models": AVAILABLE_MODELS,
        "default": DEFAULT_MODEL
    }

# ─── JD Indexing ─────────────────────────────────────────────────────────────
@app.post("/jd/index")
async def index_job_description(request: IndexJDRequest):
    if not request.jd_text.strip():
        raise HTTPException(status_code=422, detail="jd_text must not be empty.")
    
    n_chunks = index_jd(request.jd_text, request.jd_id)
    return {"jd_id": request.jd_id, "chunks_indexed": n_chunks}

# ─── Main Evaluation ─────────────────────────────────────────────────────────
@app.post("/evaluate")
async def evaluate_resume(request: EvaluationRequest):
    try:
        clean_resume = clean_pii(request.resume_text)

        jd_context = retrieve_relevant_jd_context(
            query=clean_resume[:1000],
            jd_id=request.jd_id,
            top_k=4
        )

        effective_jd = jd_context if jd_context else request.jd_text

        results = run_evaluation_chain(
            resume_text=clean_resume,
            jd_text=effective_jd,
            model_name=request.model_name
        )

        # Save to DB
        save_evaluation([{
            "Candidate Name": request.candidate_name,
            "Score": results["overall_score"],
            "Skill Match": results["breakdown"]["Skill Match"],
            "Semantic Match": results["breakdown"]["Semantic Match"],
            "Experience Relevance": results["breakdown"]["Experience Relevance"],
            "Matched Skills": ", ".join(results["matched_skills"]),
            "Missing Skills": ", ".join(results["missing_skills"]),
        }])

        # Save to vector DB
        save_candidate_to_vector_db(
            name=request.candidate_name,
            resume_text=clean_resume,
            score=results["overall_score"]
        )

        results["ragas_sample"] = build_ragas_sample(
            jd_text=effective_jd,
            resume_text=clean_resume,
            evaluation_result=results,
            retrieved_jd_chunks=[jd_context] if jd_context else []
        )

        return JSONResponse(content=results)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

# ─── Streaming Evaluation ────────────────────────────────────────────────────
@app.post("/evaluate/stream")
async def evaluate_resume_stream(request: EvaluationRequest):
    clean_resume = clean_pii(request.resume_text)
    jd_context = retrieve_relevant_jd_context(clean_resume[:1000], request.jd_id, top_k=4)
    effective_jd = jd_context if jd_context else request.jd_text

    def token_generator():
        for chunk in stream_evaluation(clean_resume, effective_jd, request.model_name):
            yield chunk

    return StreamingResponse(token_generator(), media_type="text/plain")

# ─── RAGAS Evaluation ────────────────────────────────────────────────────────
@app.post("/ragas/evaluate")
async def run_ragas_evaluation(request: RagasRequest):
    if not request.samples:
        raise HTTPException(status_code=422, detail="samples list is empty.")

    try:
        questions = [s["question"] for s in request.samples]
        answers = [s["answer"] for s in request.samples]
        contexts = [s["contexts"] for s in request.samples]
        ground_truths = [s["ground_truth"] for s in request.samples]

        scores = evaluate_pipeline(questions, answers, contexts, ground_truths)
        return {"ragas_scores": scores, "n_samples": len(request.samples)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Semantic Search ─────────────────────────────────────────────────────────
@app.post("/search")
async def semantic_search(request: SearchRequest):
    try:
        matches = search_similar_candidates(request.query, request.top_k)
        history_df = get_all_evaluations()

        enriched = []
        for match in matches:
            extra = {}
            if not history_df.empty:
                row = history_df[history_df["Candidate Name"] == match["name"]]
                if not row.empty:
                    extra["evaluated_at"] = str(row.iloc[0].get("timestamp", ""))

            enriched.append({**match, **extra})

        return {"query": request.query, "results": enriched}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000)