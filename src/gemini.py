import os
from pathlib import Path
from google import genai
from google.genai import types
import mimetypes

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
    - Do not MERGE multiple tables into single table.
    - Do not include any images URL / tag in the markdown.
    - Page numbers should be wrapped in brackets. Ex: <page_number>14<page_number> or <page_number>9/22<page_number>
    - Prefer using ☐ and ☑ for check boxes.
"""  # noqa: E501

def get_mime_type(file_path: str) -> str:
    # Try guessing mime based on file content or extension
    mime_type, _ = mimetypes.guess_type(file_path)
    # Accept only allowed types for Gemini
    if mime_type in ['application/pdf', 'image/png', 'image/jpeg', 'image/webp']:
        return mime_type
    # Fallback (default to PDF)
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return "application/pdf"
    elif ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    elif ext == ".webp":
        return "image/webp"
    else:
        raise ValueError("Unsupported file type for conversion!")

def convert_gemini(path: str, file_name: str):  # file_name kept for API compatibility
    # Determine the MIME type of the file
    try:
        mime_type = get_mime_type(path)
    except ValueError as ve:
        return f"Error: {ve}", []

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
                    mime_type=mime_type,
                ),
            ],
            config=generation_config,
        )
        output = response.text
    else:
        output = "Error: Gemini API not available."
    return output, []

# Example Usage:
# pdf_markdown, _ = convert_gemini("/path/to/file.pdf", "file.pdf")
image_markdown, _ = convert_gemini("output_data/images/1_MEDICARD.pdf-14-full.png", "1_MEDICARD.pdf-14-full.png")
