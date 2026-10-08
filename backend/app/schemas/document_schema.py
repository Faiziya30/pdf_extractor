from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ApiError


class Metadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creationDate: Optional[str] = None
    modDate: Optional[str] = None


class DocumentSummary(BaseModel):
    id: str
    filename: str
    title: Optional[str] = None
    page_count: int
    file_size: int
    metadata: Metadata
    metadata_status: str = "empty"


class Page(BaseModel):
    page_number: int
    text: str


class Heading(BaseModel):
    text: str
    level: int = Field(ge=1, le=3)
    page: int = Field(ge=1)
    confidence: float = Field(ge=0, le=1)


class DocumentResponse(BaseModel):
    success: bool = True
    document: DocumentSummary
    pages: List[Page]
    outline: List[Heading]
    processing_time_ms: int


class ResourceResponse(BaseModel):
    success: bool = True
    document: DocumentSummary


class PagesResponse(BaseModel):
    success: bool = True
    document_id: str
    pages: List[Page]


class OutlineResponse(BaseModel):
    success: bool = True
    document_id: str
    outline: List[Heading]