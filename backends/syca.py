import logging
from pathlib import Path

import sycamore
from sycamore import ExecMode
from sycamore.data import Document
from sycamore.data.document import DocumentPropertyTypes
from sycamore.functions.document import DrawBoxes, split_and_convert_to_image
from sycamore.transforms.partition import ArynPartitioner
from sycamore.utils.markdown import elements_to_markdown

from .settings import ENABLE_DEBUG_MODE

logging.getLogger().setLevel(logging.INFO)
SYCAMORE_DEBUG_PATH = Path("/tmp/sycamore")
SYCAMORE_DEBUG_PATH.mkdir(exist_ok=True)


paritioner = ArynPartitioner(
    use_partitioning_service=False,
    extract_table_structure=True,
    use_ocr=True,
    extract_images=True,
)
context = sycamore.init(
    exec_mode=ExecMode.LOCAL,
)


def image_page_filename_fn(doc: Document) -> str:
    page_num = doc.properties[DocumentPropertyTypes.PAGE_NUMBER]
    return f"page_{page_num}.png"


def convert_sycamore(path: str, file_name: str):
    docset = context.read.binary(paths=path, binary_format="pdf").partition(
        partitioner=paritioner,
    )
    debug_path = SYCAMORE_DEBUG_PATH / file_name
    debug_path.mkdir(exist_ok=True)
    image_paths = []

    doc = docset.take_all()[0]
    md = elements_to_markdown(doc.elements)

    if ENABLE_DEBUG_MODE:
        docset.flat_map(split_and_convert_to_image).map_batch(
            DrawBoxes, f_constructor_kwargs={"draw_table_cells": True}
        ).write.files(str(debug_path), filename_fn=image_page_filename_fn)
        image_paths = [str(path) for path in debug_path.glob("*.png")]
    return md, image_paths
