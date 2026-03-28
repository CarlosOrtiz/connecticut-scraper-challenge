import json
import logging

from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from scripts.common.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def generate(prompt: str):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model = settings.GEMINI_MODEL

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
        media_resolution="MEDIA_RESOLUTION_HIGH",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")


def extract_pdf_data(pdf_path: str, prompt: dict[str, Any]) -> dict[str, Any]:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    pdf_file = Path(pdf_path)

    uploaded_file = client.files.upload(file=str(pdf_file))

    instruction = (
        f"{prompt['question']}\n\n"
        "Return only valid JSON matching this schema:\n"
        f"{json.dumps(prompt['schema'], ensure_ascii=False)}"
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            uploaded_file,
            instruction,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    text = (response.text or "").strip()
    if not text:
        raise ValueError(f"Gemini returned empty response for prompt {prompt['key']}")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON for prompt %s: %s", prompt["key"], text)
        raise ValueError(f"Invalid JSON response for prompt {prompt['key']}") from exc
