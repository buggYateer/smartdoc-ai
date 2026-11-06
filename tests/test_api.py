import os
import sys
import tempfile
from pathlib import Path

# Use a throwaway SQLite database and no real API key for the tests.
_db_file = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file.as_posix()}"
os.environ["GEMINI_API_KEY"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import routes.ai as ai_routes  # noqa: E402
from database import Base, engine  # noqa: E402
from main import app  # noqa: E402
from schemas import AIAnalysisResponse  # noqa: E402
from services.agent_service import execute_tool  # noqa: E402

Base.metadata.create_all(engine)
client = TestClient(app)


@pytest.fixture
def document_id():
    response = client.post("/documents", json={"title": "Q3 Report", "content": "Revenue grew 12%.", "priority": 2})
    assert response.status_code == 201
    return response.json()["id"]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_document(document_id):
    response = client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Q3 Report"


def test_invalid_document_returns_422():
    assert client.post("/documents", json={"title": "x", "content": ""}).status_code == 422


def test_missing_document_returns_404():
    assert client.get("/documents/999999").status_code == 404


def test_upload_rejects_unsupported_type():
    response = client.post("/documents/upload", files={"file": ("a.pdf", b"%PDF", "application/pdf")})
    assert response.status_code == 400


def test_upload_rejects_non_utf8_text():
    response = client.post("/documents/upload", files={"file": ("a.txt", b"\xff\xfe\xfa", "text/plain")})
    assert response.status_code == 400


def test_upload_text_file():
    response = client.post("/documents/upload", files={"file": ("notes.txt", b"Meeting notes", "text/plain")})
    assert response.status_code == 201
    assert response.json()["content"] == "Meeting notes"


def test_analyze_saves_summary(monkeypatch, document_id):
    fake = AIAnalysisResponse(summary="Revenue up.", key_points=["+12%"], category="business", suggested_priority=2)
    monkeypatch.setattr(ai_routes, "analyze_document", lambda content: fake)

    response = client.post(f"/documents/{document_id}/analyze")
    assert response.status_code == 200
    assert client.get(f"/documents/{document_id}").json()["ai_summary"] == "Revenue up."


def test_analyze_without_api_key_returns_503(document_id):
    assert client.post(f"/documents/{document_id}/analyze").status_code == 503


def test_analyze_missing_document_returns_404():
    assert client.post("/documents/999999/analyze").status_code == 404


def test_agent_blocks_unknown_tool():
    assert "error" in execute_tool("delete_document", {"document_id": 1})


def test_agent_tool_validates_arguments():
    assert execute_tool("get_document", {"document_id": -5}) == {"error": "Tool failed safely"}


def test_agent_tool_reads_document(document_id):
    assert execute_tool("get_document", {"document_id": document_id})["title"] == "Q3 Report"
