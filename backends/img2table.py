from pathlib import Path

import cv2
from img2table.document import PDF
from img2table.ocr import SuryaOCR

from .settings import ENABLE_DEBUG_MODE

ocr = SuryaOCR(
    langs=["en"],
)
IMG2TABLE_DEBUG_PATH = Path("/tmp/img2table")
IMG2TABLE_DEBUG_PATH.mkdir(exist_ok=True)


def convert_img2table(path: str, file_name: str):
    doc = PDF(path)
    pages = doc.extract_tables(
        ocr=ocr,
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=True,
        min_confidence=50,
    )
    debug_image_paths = []

    if ENABLE_DEBUG_MODE:
        debug_path = IMG2TABLE_DEBUG_PATH / file_name
        debug_path.mkdir(exist_ok=True)

        images = doc.images
        for idx, page_number in enumerate(doc.pages or range(len(images))):
            page_image = images[idx]
            for table in pages[page_number]:
                for row in table.content.values():
                    for cell in row:
                        cv2.rectangle(
                            page_image,
                            (cell.bbox.x1, cell.bbox.y1),
                            (cell.bbox.x2, cell.bbox.y2),
                            (0, 0, 255),
                            2,
                        )
            image_path = debug_path / f"page_{idx}.png"
            debug_image_paths.append(image_path)
            cv2.imwrite(str(image_path), page_image)

    content = "\n\n".join(
        [
            (table.title if table.title else "") + "\n\n" + table.html
            for tables in pages.values()
            for table in tables
        ]
    )
    return content, debug_image_paths
