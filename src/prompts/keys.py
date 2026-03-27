from enum import Enum


class PromptKey(str, Enum):
    NORMALIZE = "normalization"
    EXTRACT_PDF_DATA = "extract_pdf_data"
