class DocumentError(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class DocumentNotFoundError(DocumentError):
    def __init__(self):
        super().__init__("DOCUMENT_NOT_FOUND", "The requested document was not found.", 404)


class InvalidDocumentError(DocumentError):
    def __init__(self, message: str = "The uploaded file is not a valid PDF."):
        super().__init__("INVALID_PDF", message, 400)


class FileTooLargeError(DocumentError):
    def __init__(self, max_size_mb: int):
        super().__init__("FILE_TOO_LARGE", f"The file exceeds the {max_size_mb} MB limit.", 413)


class EmptyDocumentError(DocumentError):
    def __init__(self):
        super().__init__("EMPTY_PDF", "The PDF does not contain any extractable text.", 422)