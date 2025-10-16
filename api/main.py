from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from retrieval import retrieve
from prompts import build_messages
from azure_clients import chat_completion
import traceback

app = FastAPI(title="RAG Student API", version="1.0")

# Autoriser toutes origines (pour test avec file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    try:
        contexts: List[Dict[str, Any]] = retrieve(req.question)
        messages = build_messages(req.question, contexts)
        answer = await chat_completion(messages)
        srcs = [c.get("source") or c.get("id", "source inconnue") for c in contexts]
        return AskResponse(answer=answer or "", sources=srcs)
    except Exception as e:
        print("=== EXCEPTION /ask ===")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "ok"}
