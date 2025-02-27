import functools
from pathlib import Path

from matplotlib import font_manager
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.pdf_image.analysis import bbox_visualisation

from .settings import ENABLE_DEBUG_MODE

UNSTRUCTURED_DEBUG_PATH = Path("/tmp/unstructured")


def convert_elements_to_markdown(elements):
    lines = []

    for e in elements:
        if e.category == "Title":
            line = f"\n# {e.text}\n"
        elif e.category == "ListItem":
            line = f"- {e.text}"
        elif e.category == "Table":
            line = f"\n{e.metadata.text_as_html}\n"
        elif e.category == "UncategorizedText":
            line = ""
        elif e.category == "Image":
            # base64 image
            line = f"![{e.text}](data:image/jpeg;base64," f"{e.metadata.image_base64})"
        else:
            line = e.text

        lines.append(line)

    md = "\n".join(lines)
    return md


@functools.lru_cache(maxsize=None)
def get_font():
    preferred_fonts = ["Arial.ttf", "DejaVuSans.ttf"]
    available_fonts = font_manager.findSystemFonts()
    if not available_fonts:
        raise ValueError("No fonts available")
    for font in preferred_fonts:
        for available_font in available_fonts:
            if font in available_font:
                return available_font

    return available_fonts[0]


# monkey patch
bbox_visualisation.get_font = get_font


def convert_unstructured(path: str, file_name: str):
    elements = partition_pdf(
        filename=path,
        # mandatory to use ``hi_res`` strategy
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=True,
        analysis=ENABLE_DEBUG_MODE,
        analyzed_image_output_dir_path=UNSTRUCTURED_DEBUG_PATH,
    )
    text = convert_elements_to_markdown(elements)
    debug_image_dir = UNSTRUCTURED_DEBUG_PATH / "analysis" / file_name / "bboxes"
    if debug_image_dir.exists():
        debug_image_paths = [
            path for path in debug_image_dir.iterdir() if "od_model" in path.stem
        ]
    else:
        debug_image_paths = []

    return text, debug_image_paths
