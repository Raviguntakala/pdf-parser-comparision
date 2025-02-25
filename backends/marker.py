import base64
import io
import re
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.settings import settings

# Marker init
marker_converter = PdfConverter(
    artifact_dict=create_model_dict(),
    config={
        "debug_pdf_images": True,
    },
)


def img_to_html(img, img_alt):
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=settings.OUTPUT_IMAGE_FORMAT)
    img_bytes_value = img_bytes.getvalue()
    encoded = base64.b64encode(img_bytes_value).decode()
    img_html = (
        f'<img src="data:image/{settings.OUTPUT_IMAGE_FORMAT.lower()}'
        f';base64,{encoded}" alt="{img_alt}" style="max-width: 100%;">'
    )
    return img_html


def markdown_insert_images(markdown, images):
    image_tags = re.findall(
        r'(!\[(?P<image_title>[^\]]*)\]\((?P<image_path>[^\)"\s]+)\s*([^\)]*)\))',
        markdown,
    )

    for image in image_tags:
        image_markdown = image[0]
        image_alt = image[1]
        image_path = image[2]
        if image_path in images:
            markdown = markdown.replace(
                image_markdown, img_to_html(images[image_path], image_alt)
            )
    return markdown


def convert_marker(path: str, file_name: str):
    rendered = marker_converter(path)
    text, _, images = text_from_rendered(rendered)
    text = markdown_insert_images(text, images)
    debug_image_dir = Path(rendered.metadata.get("debug_data_path"))
    debug_image_paths = [
        path for path in debug_image_dir.iterdir() if "pdf_page" in path.stem
    ]

    return text, debug_image_paths
