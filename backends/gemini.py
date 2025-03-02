import os
from pathlib import Path

from google import genai
from google.genai import types

# Create a client
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
except Exception as e:
    print(e)
    client = None

MODEL_NAME = "gemini-2.0-flash"
PROMPT = """
Convert the following document to markdown, preserving header, table and figure structure as much as possible.
Return only the markdown with no explanation text. Do not include delimiters like ```markdown or ```html.

RULES:
    - You must include all information on the page. Do not exclude headers, footers, or subtext.
    - Return tables in Markdown format.
    - Must format headers / sub-headers in Markdown format (#, ##, etc).
    - Attempt to merge line-breaks in to coherent paragraphs.
    - Charts & infographics must be interpreted to a text-based markdown format. Prefer table format when applicable.
    - Do not include any images URL / tag in the markdown.
    - Page numbers should be wrapped in brackets. Ex: <page_number>14<page_number> or <page_number>9/22<page_number>
    - Prefer using ☐ and ☑ for check boxes.
"""  # noqa: E501


def convert_gemini(path: str, file_name: str):
    # Generate a structured response using the Gemini API
    generation_config = types.GenerationConfig(
        max_output_tokens=8192,
    ).to_json_dict()
    if client:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                PROMPT,
                types.Part.from_bytes(
                    data=Path(path).read_bytes(),
                    mime_type="application/pdf",
                ),
            ],
            config=generation_config,
        )
        output = response.text
    else:
        output = "Error: Gemini API not available."
    # Convert the response to the pydantic model and return it
    return output, []
