import base64
import os
import re
from pathlib import Path

import pymupdf
from magic_pdf.data.data_reader_writer import FileBasedDataReader
from magic_pdf.tools.common import do_parse, prepare_env

from .settings import ENABLE_DEBUG_MODE

MINERU_DEBUG_PATH = Path("/tmp/mineru")
MINERU_DEBUG_PATH.mkdir(exist_ok=True)


def read_fn(path):
    disk_rw = FileBasedDataReader(MINERU_DEBUG_PATH)
    return disk_rw.read(path)


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def replace_image_with_base64(markdown_text, image_dir_path):
    pattern = r"\!\[(?:[^\]]*)\]\(([^)]+)\)"

    def replace(match):
        relative_path = match.group(1)
        full_path = os.path.join(image_dir_path, relative_path)
        base64_image = image_to_base64(full_path)
        return f"![{relative_path}](data:image/jpeg;base64,{base64_image})"

    return re.sub(pattern, replace, markdown_text)


def do_process_mineru(input_path, output_dir):
    file_name = Path(input_path).stem
    output_dir = Path(output_dir)

    pdf_data = read_fn(input_path)
    parse_method = "auto"
    local_image_dir, local_md_dir = prepare_env(output_dir, file_name, parse_method)
    do_parse(
        output_dir,
        file_name,
        pdf_data,
        [],
        parse_method,
        debug_able=False,
        f_dump_orig_pdf=False,
        f_draw_layout_bbox=ENABLE_DEBUG_MODE,
        f_draw_char_bbox=ENABLE_DEBUG_MODE,
        formula_enable=False,
        table_enable=True,
    )
    return local_md_dir, file_name


def convert_mineru(path: str, file_name: str):
    debug_image_paths = []
    output_path = MINERU_DEBUG_PATH / file_name
    output_path.mkdir(exist_ok=True)

    local_md_dir, _ = do_process_mineru(path, output_path)
    local_md_dir = Path(local_md_dir)

    with open(local_md_dir / f"{file_name}.md", "r") as file:
        text = file.read()

    text = replace_image_with_base64(text, local_md_dir)

    debug_pdf = str(local_md_dir / (file_name + "_layout.pdf"))

    if Path(debug_pdf).exists():
        doc = pymupdf.open(debug_pdf)  # open document
        for page in doc:  # iterate through the pages
            pix = page.get_pixmap()  # render page to an image
            page_debug_path = str(output_path / ("page-%i.png" % page.number))
            debug_image_paths.append(page_debug_path)
            pix.save(page_debug_path)  # store image as a PNG

    return text, debug_image_paths
