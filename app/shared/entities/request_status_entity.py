# ruff: noqa: F401
from typing import List
from datetime import datetime
from uuid import UUID, uuid4
from app.shared.entities.requestEntity import Request
from sqlmodel import Field, Relationship, SQLModel


class RequestStatus(SQLModel, table=True):
    __tablename__ = "request_statuses"
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="ID único del estado de la solicitud.",
    )
    name: str = Field(
        nullable=False, index=True, description="Nombre del estado de la solicitud."
    )
    code: str = Field(
        nullable=False, index=True, description="Código del estado de la solicitud."
    )
    description: str = Field(
        nullable=False, description="Descripción del estado de la solicitud."
    )
    is_active: bool = Field(
        default=True, description="Indica si el estado está activo."
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Fecha de creación del estado."
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Fecha de actualización del estado."
    )

    requests: List["Request"] = Relationship(back_populates="status")
