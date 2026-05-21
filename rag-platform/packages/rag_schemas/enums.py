from enum import StrEnum


class DocumentStage(StrEnum):
    OTR = "OTR"
    TEO = "TEO"
    PD = "PD"
    RD = "RD"


class ElementType(StrEnum):
    TEXT = "text"
    TABLE = "table"
    NOTE = "note"
    SPECIFICATION = "specification"
    TITLE = "title"
    STAMP = "stamp"
    DRAWING_ZONE = "drawing_zone"
    SECTION = "section"
    SUBSECTION = "subsection"
    REQUIREMENT = "requirement"
    TITLE_SHEET = "title_sheet"
    VOLUME_INDEX = "volume_index"
    DOCUMENT_REGISTER = "document_register"
    CALCULATION = "calculation"
    DRAWING_SHEET = "drawing_sheet"


class JobStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    TOKENIZING = "tokenizing"
    EMBEDDING = "embedding"
    INDEXED = "indexed"
    FAILED = "failed"


class ProcessingStage(StrEnum):
    PARSE = "parse"
    TOKENIZE = "tokenize"
    EMBED = "embed"
    INDEX = "index"


class TokenQuality(StrEnum):
    COMPLETE = "complete"
    WEAK = "weak"
    EMPTY = "empty"
    OCR_RISK = "ocr_risk"
