from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Marker init
marker_converter = PdfConverter(
    artifact_dict=create_model_dict(),
    config={
        "debug_pdf_images": True,
    },
)


def convert_marker(path: str, file_name: str):
    rendered = marker_converter(path)
    text, _, images = text_from_rendered(rendered)
    debug_image_dir = Path(rendered.metadata.get("debug_data_path"))
    debug_image_paths = [
        path for path in debug_image_dir.iterdir() if "pdf_page" in path.stem
    ]

    return text, debug_image_paths
