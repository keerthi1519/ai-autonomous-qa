def read_txt(file_path: str) -> str:
    """
    Read a text file and return its content.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()