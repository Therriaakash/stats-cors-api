
import os
import time
import uuid
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

EMAIL = "22f3002796@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-qydnjo.example.com"

app = FastAPI(title="Statistics and Strict CORS API")

# Only the assigned origin is allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


@app.middleware("http")
async def request_metadata(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    elapsed = max(0.0, time.perf_counter() - start)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        parts = values.split(",")
        if not parts or any(not part.strip() for part in parts):
            raise ValueError("Empty value")
        numbers = [int(part.strip()) for part in parts]
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="values must be comma-separated integers",
        )

    if not numbers:
        raise HTTPException(status_code=422, detail="At least one value is required")

    total = sum(numbers)
    count = len(numbers)

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / count,
    }


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
