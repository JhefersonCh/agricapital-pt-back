from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from app.shared.entities.request_status_entity import RequestStatus
from app.shared.entities.credit_type_enity import CreditType


class RequestBase(SQLModel):
    client_id: UUID = Field(
        nullable=False,
        index=True,
        description="ID del cliente que realiza la solicitud.",
    )
    requested_amount: float = Field(
        ge=0, description="Monto solicitado por el cliente."
    )
    term_months: int = Field(gt=0, description="Plazo del crédito en meses.")
    annual_interest_rate: float = Field(
        ge=0, description="Tasa de interés anual acordada."
    )
    credit_type_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="credit_types.id",
        description="ID del tipo de crédito solicitado.",
    )
    status_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="request_statuses.id",
        description="ID del estado actual de la solicitud.",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        description="Fecha de creación de la solicitud.",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        description="Última fecha de actualización de la solicitud.",
    )


class Request(RequestBase, table=True):
    __tablename__ = "requests"
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="ID único de la solicitud.",
    )
    approved_amount: Optional[float] = Field(
        default=None, ge=0, description="Monto final aprobado, si aplica."
    )
    approved_at: Optional[datetime] = Field(
        default=None, description="Fecha de aprobación de la solicitud."
    )
    analyst_id: Optional[UUID] = Field(
        default=None, index=True, description="ID del analista que aprobó o rechazó."
    )
    rejection_reason: Optional[str] = Field(
        default=None, max_length=500, description="Razón si la solicitud fue rechazada."
    )
    risk_score: Optional[float] = Field(
        default=None, ge=0, le=1, description="Puntuación de riesgo del cliente (0-1)."
    )
    credit_type: Optional[CreditType] = Relationship(back_populates="requests")
    status: Optional[RequestStatus] = Relationship(back_populates="requests")
