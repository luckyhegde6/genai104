from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .llm_client import OllamaClient
from .review_engine import run_review
from .db import save_review, fetch_review

router = APIRouter()

class ReviewRequest(BaseModel):
    diff: str
    persona: str = "mentor"
    mock: bool = True

@router.post("/reviews")
def create_review(payload: ReviewRequest):
    client = OllamaClient(mock=payload.mock)
    try:
        comments = run_review(payload.diff, payload.persona, client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rid = save_review(payload.diff, payload.persona, comments, comments)
    return {"review_id": rid, "comments_count": len(comments)}

@router.get("/reviews/{review_id}")
def get_review(review_id: int):
    r = fetch_review(review_id)
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return r
