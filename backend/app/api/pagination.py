from typing import Generic, List, TypeVar, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Standard query parameters for paginated list endpoints.
    """

    page: int = Field(default=1, ge=1, description="1-based page index")
    size: int = Field(default=10, ge=1, le=100, description="Page limit size")


class PageMetadata(BaseModel):
    """
    Enclosed pagination metadata parameters.
    """

    total: int = Field(..., description="Total database record count")
    page: int = Field(..., description="Current 1-based page index")
    size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total computed pages")
    has_next: bool = Field(..., description="True if next page exists")
    has_prev: bool = Field(..., description="True if previous page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Enveloped paginated HTTP response payload.
    """

    success: bool = True
    message: str = "Records fetched successfully"
    data: List[T]
    metadata: PageMetadata
