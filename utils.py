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
def trim_pages(pdf_path, output_path, start_page=0, trim_pages=5):
    doc = pymupdf.open(pdf_path)
    parent_dir_name = Path(pdf_path).parent.name
    output_file_path = Path(output_path) / f"{parent_dir_name}.pdf"

    num_pages = len(doc)
    if num_pages > trim_pages:
        to_select = list(range(start_page, min(start_page + trim_pages, num_pages)))
        doc.select(to_select)
        doc.ez_save(output_file_path)
        print("Trimmed pdf to with pages", to_select, "path", output_file_path)
    else:
        copy2(pdf_path, str(output_file_path))

    return str(output_file_path)


def fix_problematic_imports():
    import sys
    import types

    # Create a fake 'UnimernetModel' class inside a fake 'Unimernet' module
    fake_unimernet_module = types.ModuleType(
        "magic_pdf.model.sub_modules.mfr.unimernet.Unimernet"
    )
    fake_unimernet_module.UnimernetModel = type(  # type: ignore
        "UnimernetModel", (), {}
    )

    # Register fake module in sys.modules
    sys.modules[
        "magic_pdf.model.sub_modules.mfr.unimernet.Unimernet"
    ] = fake_unimernet_module


def prepare_env_mineru():
    import json
    import os

    import nltk

    # download nltk data
    nltk.download("punkt_tab")
    nltk.download("averaged_perceptron_tagger_eng")

    home_path = Path.home()
    config_path = home_path / "magic-pdf.json"
    # skip download if config file exists
    if config_path.exists():
        print("Config file exists, skipping models download")
        return

    # download models
    os.system(
        "wget https://github.com/opendatalab/MinerU/raw/"
        "dev/scripts/download_models_hf.py -O download_models_hf.py"
    )
    os.system("python3 download_models_hf.py")

    with open(config_path, "r") as file:
        data = json.load(file)

    data["device-mode"] = "cuda"
    with open(config_path, "w") as file:
        json.dump(data, file, indent=4)

    os.system(
        f"cp -r resources {home_path}/.local/lib/"
        "python3.10/site-packages/magic_pdf/resources"
    )

    # copy OCR model weight
    target_model_path = home_path / ".paddleocr"
    os.system(f"cp -r paddleocr {target_model_path}")
