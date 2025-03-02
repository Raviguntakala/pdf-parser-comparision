import asyncio
import re
from pathlib import Path

from pyzerox import zerox


def remove_images_from_markdown(markdown_text):
    # remove <image> and ![image](path) from markdown
    markdown_text = re.sub(r"<img[^>]*>", "", markdown_text)
    markdown_text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", markdown_text)
    return markdown_text


ZEROX_DEBUG_PATH = Path("/tmp/zerox_debug")
ZEROX_DEBUG_PATH.mkdir(exist_ok=True)
MODEL_NAME = "gemini/gemini-2.0-flash"


def clean_up_html_code_block(text: str):
    # remove ```html and ``` from text
    text = text.replace("```html", "")
    text = text.replace("```", "")
    return text


def convert_zerox(path: str, file_name: str):
    output_dir = ZEROX_DEBUG_PATH / file_name
    output_dir.mkdir(exist_ok=True)

    async def async_convert():
        return await zerox(
            concurrency=4,
            file_path=path,
            model=MODEL_NAME,
            output_dir=output_dir,
        )

    output = asyncio.run(async_convert())
    output_text = "\n\n".join(page.content for page in output.pages)
    output_text = clean_up_html_code_block(output_text)
    output_text = remove_images_from_markdown(output_text)
    return output_text, []
