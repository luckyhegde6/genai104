from fastapi import FastAPI
from .api_reviews import router
from .db import init_db

app = FastAPI(title="Code Review Assistant (local)")
app.include_router(router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "message": "Code Review Assistant"}
