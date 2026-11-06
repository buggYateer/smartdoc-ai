import logging

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import engine
from models import Document
from settings import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)
MAX_STEPS = 5


def list_documents_tool():
    with Session(engine) as db:
        documents = db.query(Document).all()
        return [{"id": item.id, "title": item.title, "priority": item.priority} for item in documents]


def get_document_tool(document_id):
    if not isinstance(document_id, int) or document_id <= 0:
        raise ValueError("document_id must be positive")
    with Session(engine) as db:
        document = db.get(Document, document_id)
        if document is None:
            return {"status": "not_found"}
        return {"id": document.id, "title": document.title, "content": document.content, "priority": document.priority}


def search_documents_tool(query):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must not be empty")
    with Session(engine) as db:
        items = db.query(Document).filter(
            or_(Document.title.ilike(f"%{query}%"), Document.content.ilike(f"%{query}%"))
        ).all()
        return [{"id": item.id, "title": item.title} for item in items]


TOOLS = {"list_documents": list_documents_tool, "get_document": get_document_tool, "search_documents": search_documents_tool}


class GetDocumentInput(BaseModel):
    document_id: int = Field(gt=0)


class SearchDocumentsInput(BaseModel):
    query: str = Field(min_length=1)


VALIDATORS = {
    "list_documents": None,
    "get_document": GetDocumentInput,
    "search_documents": SearchDocumentsInput,
}


def execute_tool(name, arguments):
    if name not in TOOLS:
        logger.warning("Blocked tool call: %s", name)
        return {"error": f"Tool '{name}' is not allowed"}
    try:
        validator = VALIDATORS[name]
        values = validator(**(arguments or {})).model_dump() if validator else {}
        result = TOOLS[name](**values)
        logger.info("tool=%s success=True", name)
        return result
    except Exception:
        logger.info("tool=%s success=False", name)
        return {"error": "Tool failed safely"}


def ask_agent(message):
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=GEMINI_API_KEY)

    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="list_documents",
                    description="List all available documents with their ids, titles, and priorities.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={},
                    ),
                ),
                types.FunctionDeclaration(
                    name="get_document",
                    description="Get a document by its positive integer id.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "document_id": types.Schema(
                                type=types.Type.INTEGER,
                                description="Positive document id.",
                            )
                        },
                        required=["document_id"],
                    ),
                ),
                types.FunctionDeclaration(
                    name="search_documents",
                    description="Search documents by title or content.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "query": types.Schema(
                                type=types.Type.STRING,
                                description="Non-empty search query.",
                            )
                        },
                        required=["query"],
                    ),
                ),
            ]
        )
    ]

    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=(
            "You are a read-only document assistant. "
            "You may only use the provided document tools. "
            "Never invent document information. "
            "Use tool results to answer the user."
        ),
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )
    ]

    for _ in range(MAX_STEPS):
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config,
        )

        model_content = response.candidates[0].content
        calls = [part.function_call for part in model_content.parts or [] if part.function_call]

        if not calls:
            return response.text

        # Run every tool the model asked for in this step, then send all results back.
        contents.append(model_content)
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=call.name,
                        response={"result": execute_tool(call.name, dict(call.args or {}))},
                    )
                    for call in calls
                ],
            )
        )

    raise RuntimeError("Agent exceeded MAX_STEPS")