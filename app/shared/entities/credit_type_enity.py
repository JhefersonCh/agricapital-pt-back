# ruff: noqa: F401
from typing import List
from datetime import datetime
from uuid import UUID, uuid4
from app.shared.entities.requestEntity import Request
from sqlmodel import Field, Relationship, SQLModel


class CreditType(SQLModel, table=True):
    __tablename__ = "credit_types"
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="ID único del tipo de crédito.",
    )
    name: str = Field(
        nullable=False, index=True, description="Nombre del tipo de crédito."
    )
    code: str = Field(
        nullable=False, index=True, description="Código del tipo de crédito."
    )
    description: str = Field(
        nullable=False, description="Descripción del tipo de crédito."
    )
    is_active: bool = Field(
        default=True, description="Indica si el tipo de crédito está activo."
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Fecha de creación del tipo de crédito.",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Fecha de actualización del tipo de crédito.",
    )

    requests: List["Request"] = Relationship(back_populates="credit_type")
