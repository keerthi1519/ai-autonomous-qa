import os

from app.readers.pdf_reader import read_pdf
from app.readers.docx_reader import read_docx
from app.readers.txt_reader import read_txt


class RequirementService:
    """
    Service responsible only for reading requirement documents.
    """

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from a requirement document.

        Supported file formats:
        - PDF
        - DOCX
        - TXT
        """

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            return read_pdf(file_path)

        elif extension == ".docx":
            return read_docx(file_path)

        elif extension == ".txt":
            return read_txt(file_path)

        else:
            raise ValueError(
                f"Unsupported file format: {extension}"
            )