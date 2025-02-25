import functools
import re
from pathlib import Path
from shutil import copy2

import pymupdf


def remove_images_from_markdown(markdown_text):
    # remove <image> and ![image](path) from markdown
    markdown_text = re.sub(r"<img[^>]*>", "", markdown_text)
    markdown_text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", markdown_text)
    return markdown_text


@functools.lru_cache(maxsize=None)
def trim_pages(pdf_path, output_path, trim_pages=5):
    doc = pymupdf.open(pdf_path)
    parent_dir_name = Path(pdf_path).parent.name
    output_file_path = Path(output_path) / f"{parent_dir_name}.pdf"

    num_pages = len(doc)
    if num_pages > trim_pages:
        to_select = list(range(trim_pages))
        doc.select(to_select)
        doc.ez_save(output_file_path)
        print("Trimmed pdf to with pages", to_select, "path", output_file_path)
    else:
        copy2(pdf_path, str(output_file_path))

    return str(output_file_path)
