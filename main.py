from fastapi import FastAPI

from routes.ai import router as ai_router
from routes.documents import router as documents_router

# Database schema is managed by Alembic: run `python -m alembic upgrade head`.
app = FastAPI(title="SmartDoc AI", description="AI-powered documents API", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(documents_router)
app.include_router(ai_router)
