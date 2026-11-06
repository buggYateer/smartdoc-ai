from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from database import engine
from models import Document
from schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
def list_documents():
    with Session(engine) as db:
        return db.query(Document).all()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate):
    with Session(engine) as db:
        document = Document(**payload.model_dump())
        db.add(document)
        db.commit()
        db.refresh(document)
        return document


@router.get("/{document_id}", response_model=DocumentResponse, responses={404: {"description": "Document not found"}})
def get_document(document_id: int):
    with Session(engine) as db:
        document = db.get(Document, document_id)
        if document is None:
            raise HTTPException(404, "Document not found")
        return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, payload: DocumentCreate):
    with Session(engine) as db:
        document = db.get(Document, document_id)
        if document is None:
            raise HTTPException(404, "Document not found")
        for key, value in payload.model_dump().items():
            setattr(document, key, value)
        db.commit()
        db.refresh(document)
        return document


@router.delete("/{document_id}")
def delete_document(document_id: int):
    with Session(engine) as db:
        document = db.get(Document, document_id)
        if document is None:
            raise HTTPException(404, "Document not found")
        db.delete(document)
        db.commit()
        return {"message": "Document deleted"}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(400, "Only text/plain is supported")
    try:
        content = (await file.read()).decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8 encoded text")
    try:
        payload = DocumentCreate(title=(file.filename or "uploaded.txt")[:120], content=content)
    except ValidationError as error:
        raise HTTPException(422, error.errors(include_url=False, include_context=False))
    return create_document(payload)
