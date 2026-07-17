from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel

DataType = TypeVar("DataType")


class APIResponse(BaseModel, Generic[DataType]):
    """
    Standardized top-level API envelope structure.
    Used uniformly across all HTTP responses.
    """

    success: bool
    message: str
    data: Optional[DataType] = None
    metadata: Optional[dict[str, Any]] = None
