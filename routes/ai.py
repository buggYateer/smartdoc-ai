import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import engine
from models import Document
from schemas import AIAnalysisResponse, AgentRequest, AgentResponse
from services.agent_service import ask_agent
from services.gemini_service import analyze_document


logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai"])


@router.post(
    "/documents/{document_id}/analyze",
    response_model=AIAnalysisResponse,
)
def analyze(document_id: int):
    with Session(engine) as db:
        document = db.get(Document, document_id)

        if document is None:
            raise HTTPException(404, "Document not found")

        try:
            result = analyze_document(document.content)
        except Exception:
            logger.exception("Gemini analysis failed for document %s", document_id)
            raise HTTPException(503, "AI analysis is unavailable")

        document.ai_summary = result.summary
        db.commit()

        return result


@router.post("/agent/ask", response_model=AgentResponse)
def ask(payload: AgentRequest):
    try:
        return {"answer": ask_agent(payload.message)}
    except Exception:
        logger.exception("Agent request failed")
        raise HTTPException(503, "Agent request failed")
