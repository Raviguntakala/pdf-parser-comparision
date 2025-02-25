from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

DOCLING_DEBUG_PATH = Path("/tmp/docling")

# Docling settings
accelerator_options = AcceleratorOptions(num_threads=8, device=AcceleratorDevice.AUTO)
pipeline_options = PdfPipelineOptions()
pipeline_options.accelerator_options = accelerator_options
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2.0

# debug visualization settings
settings.debug.debug_output_path = str(DOCLING_DEBUG_PATH)
settings.debug.visualize_layout = True
settings.debug.visualize_tables = True

# Docling init
docling_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)


def convert_docling(path: str, file_name: str):
    result = docling_converter.convert(path)
    text = result.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    debug_image_dir = DOCLING_DEBUG_PATH / f"debug_{file_name}"
    debug_image_paths = [
        path for path in debug_image_dir.iterdir() if path.suffix == ".png"
    ]

    return text, debug_image_paths
