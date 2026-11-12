from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder

# Ensure imports such as `from rag...` resolve when launched from the repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.crag_llama_pipeline import CRAGLlamaPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline = CRAGLlamaPipeline()
    yield
    app.state.pipeline.close()


app = FastAPI(
    title="CIF Investigation API",
    version="1.0.0",
    description="API wrapper for the existing CIF reasoning pipeline.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvestigationRequest(BaseModel):
    query: str = Field(min_length=8, max_length=2000)


@app.get("/api/health")
async def health():
    return {"status": "online", "service": "CIF Investigation API"}


@app.post("/api/investigate")
async def investigate(payload: InvestigationRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Query cannot be empty.")

    try:
        # The pipeline is synchronous and may perform database/model I/O.
        result: Any = await run_in_threadpool(
            app.state.pipeline.run,
            query,
        )
        return jsonable_encoder(result)
    except Exception as exc:
        # Keep the detailed exception in the server terminal, not the browser.
        print(f"[CIF API] Investigation failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed ({type(exc).__name__}). Check the API terminal.",
        ) from exc
