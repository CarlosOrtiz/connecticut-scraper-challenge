import os
from google import genai
from google.genai import types

from scripts.common.config import get_settings

settings = get_settings()


def generate(prompt: str):
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY"),
    )

    model = (
        settings.GEMINI_MODEL
        or os.environ.get("GEMINI_MODEL")
        or "gemini-3-flash-preview"
    )
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


if __name__ == "__main__":
    generate("Hello, how are you?")
