import json

from google import genai
from google.genai import types

from schemas import AIAnalysisResponse
from settings import GEMINI_API_KEY, GEMINI_MODEL


def analyze_document(content):
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY")

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=content,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a careful document analyst. "
                "Summarize and classify only the provided document. "
                "Do not invent missing facts. "
                "Return ONLY valid JSON with exactly these fields: "
                "summary, key_points, category, suggested_priority. "
                "category MUST be one of: technical, business, general. "
                "suggested_priority MUST be an INTEGER from 1 to 5. "
                "NEVER return words such as Low, Medium, or High for suggested_priority."
            ),
            response_mime_type="application/json",
        ),
    )

    return AIAnalysisResponse(**json.loads(response.text))