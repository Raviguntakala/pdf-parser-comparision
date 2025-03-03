# flake8: noqa
from .docling import convert_docling
from .gemini import convert_gemini
from .gmft import convert_gmft
from .img2table import convert_img2table
from .marker import convert_marker
from .mineru import convert_mineru
from .syca import convert_sycamore
from .unstructured import convert_unstructured

# from .zerox import convert_zerox

__all__ = [
    "convert_docling",
    "convert_marker",
    "convert_mineru",
    "convert_unstructured",
    "convert_gemini",
    # "convert_zerox",
    "convert_img2table",
    "convert_gmft",
    "convert_sycamore",
]

SUPPORTED_METHODS = [
    "PyMuPDF",
    "Docling",
    "Marker",
    "MinerU",
    "Unstructured",
    "Gemini (API)",
    "Img2Table (table-only)",
    "GMFT (table-only)",
    "Sycamore",
    # "Zerox"
]
SUPPORTED_METHODS_METADATA = {
    "Unstructured": {
        "name": "Unstructured",
        "description": "Open-Source Pre-Processing Tools for Unstructured Data.",
        "url": "https://github.com/Unstructured-IO/unstructured",
        "documentation": "https://docs.unstructured.io/welcome",
    },
    "Marker": {
        "name": "Marker",
        "description": "Marker converts documents to markdown, JSON, and HTML quickly and accurately.",
        "url": "https://github.com/VikParuchuri/marker",
        "documentation": "https://github.com/VikParuchuri/marker",
    },
    "MinerU": {
        "name": "MinerU",
        "description": "A high-quality tool for convert PDF to Markdown and JSON.",
        "url": "https://github.com/opendatalab/MinerU",
        "documentation": "https://github.com/opendatalab/MinerU",
    },
    "Docling": {
        "name": "Docling",
        "description": "Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.",
        "url": "https://github.com/DS4SD/docling",
        "documentation": "https://ds4sd.github.io/docling/",
    },
    "PyMuPDF": {
        "name": "PyMuPDF",
        "description": "PyMuPDF is a high performance Python library for data extraction, analysis, conversion & manipulation of PDF (and other) documents.",
        "url": "https://github.com/pymupdf/PyMuPDF",
        "documentation": "https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html",
    },
    "PyMuPDF": {
        "name": "PyMuPDF",
        "description": "PyMuPDF is a high performance Python library for data extraction, analysis, conversion & manipulation of PDF (and other) documents.",
        "url": "https://github.com/pymupdf/PyMuPDF",
        "documentation": "https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html",
    },
    "Gemini (API)": {
        "name": "Gemini",
        "description": "Using Gemini multimodal API to parse PDF to markdown.",
        "url": None,
        "documentation": "https://ai.google.dev/gemini-api/docs/document-processing?lang=python",
    },
    "Img2Table (table-only)": {
        "name": "Img2Table",
        "description": "img2table is a table identification and extraction Python Library for PDF and images, based on OpenCV image processing.",
        "url": "https://github.com/xavctn/img2table",
        "documentation": "https://github.com/xavctn/img2table",
    },
    "GMFT (table-only)": {
        "name": "GMFT",
        "description": "Lightweight, performant, deep table extraction.",
        "url": "https://github.com/conjuncts/gmft",
        "documentation": "https://github.com/conjuncts/gmft",
    },
    "Sycamore": {
        "name": "Sycamore",
        "description": "Sycamore is an open source, AI-powered document processing engine for ETL, RAG, LLM-based applications, and analytics on unstructured data.",
        "url": "https://github.com/aryn-ai/sycamore",
        "documentation": "https://sycamore.readthedocs.io/en/stable/",
    },
}
