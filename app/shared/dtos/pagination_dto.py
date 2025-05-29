from pydantic import BaseModel, Field
from typing import List, Any


class PaginationMeta(BaseModel):
    page: int = Field(..., description="Número de la página actual.")
    per_page: int = Field(..., description="Número de elementos por página.")
    total_items: int = Field(..., description="Número total de elementos disponibles.")
    total_pages: int = Field(..., description="Número total de páginas disponibles.")
    has_previous_page: bool = Field(
        ..., description="Indica si hay una página anterior."
    )
    has_next_page: bool = Field(..., description="Indica si hay una página siguiente.")


class PaginatedRequestsResponse(BaseModel):
    data: List[Any]
    pagination: PaginationMeta

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 25,
                    "total_pages": 3,
                    "has_previous_page": False,
                    "has_next_page": True,
                },
            }
        }
