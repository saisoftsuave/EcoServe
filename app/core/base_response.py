from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

# Define a generic type variable
T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None

    class Config:
        from_attributes = True