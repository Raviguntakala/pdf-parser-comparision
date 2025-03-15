from pypdf import PdfReader


def convert_pypdf(path: str, file_name: str):
    pdf = PdfReader(path)
    pages = pdf.pages

    text = "\n\n".join([page.extract_text(0) for page in pages])

    return text, []
