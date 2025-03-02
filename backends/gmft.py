from pathlib import Path

from gmft.auto import AutoFormatConfig, AutoTableFormatter, CroppedTable, TableDetector
from gmft.pdf_bindings import PyPDFium2Document

from .settings import ENABLE_DEBUG_MODE

detector = TableDetector()
config = AutoFormatConfig()
config.semantic_spanning_cells = True  # [Experimental] better spanning cells
config.enable_multi_header = True  # multi-headers
formatter = AutoTableFormatter(config)


GMFT_DEBUG_PATH = Path("/tmp/gmft")
GMFT_DEBUG_PATH.mkdir(exist_ok=True)


def ingest_pdf(pdf_path) -> list[CroppedTable]:
    doc = PyPDFium2Document(pdf_path)

    tables = []
    for page in doc:
        tables += detector.extract(page)
    return tables


def convert_gmft(path: str, file_name: str):
    tables = ingest_pdf(path)
    formatted_tables = []
    debug_image_paths = []

    debug_path = GMFT_DEBUG_PATH / file_name
    debug_path.mkdir(exist_ok=True)

    for idx, table in enumerate(tables):
        ft = formatter.extract(
            table,
            dpi=72 * 2,
        )
        df = ft.df()
        if df is not None:
            html = df.fillna("").to_html(
                index=False,
            )
            formatted_tables.append(html)

        if ENABLE_DEBUG_MODE:
            image_path = debug_path / f"table_{idx}.png"
            ft.image().save(image_path)
            debug_image_paths.append(image_path)

    content = "\n\n".join(formatted_tables)
    return content, debug_image_paths
