from docx import Document


def read_docx(file_path: str) -> str:
    """
    Extract text from a DOCX document.
    """

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text