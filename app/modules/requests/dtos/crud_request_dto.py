from datetime import datetime
from typing import Optional
from uuid import UUID

from app.shared.entities.credit_type_enity import CreditType
from app.shared.entities.request_status_entity import RequestStatus

from pydantic import BaseModel, Field as PydanticField


class BaseRequestSchema(BaseModel):
    client_id: UUID = PydanticField(
        ...,
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        description="ID del cliente que realiza la solicitud.",
    )
    requested_amount: float = PydanticField(
        ..., example=1000.0, ge=0, description="Monto solicitado."
    )
    term_months: int = PydanticField(
        ..., example=12, gt=0, description="Plazo en meses."
    )
    annual_interest_rate: float = PydanticField(
        ..., example=0.1, ge=0, description="Tasa de interés anual."
    )
    credit_type_id: UUID = PydanticField(
        ...,
        example="b1c2d3e4-f5a6-7890-1234-567890abcdef",
        description="ID del tipo de crédito.",
    )
    status_id: UUID = PydanticField(
        ...,
        example="c1d2e3f4-a5b6-7890-1234-567890abcdef",
        description="ID del estado de la solicitud.",
    )

    class Config:
        from_attributes = True


class RequestCreate(BaseRequestSchema):
    pass


class RequestUpdate(BaseModel):
    requested_amount: Optional[float] = PydanticField(
        None, ge=0, description="Nuevo monto solicitado."
    )
    term_months: Optional[int] = PydanticField(
        None, gt=0, description="Nuevo plazo del crédito en meses."
    )
    annual_interest_rate: Optional[float] = PydanticField(
        None, ge=0, description="Nueva tasa de interés anual."
    )
    credit_type_id: Optional[UUID] = PydanticField(
        None, description="Nuevo ID del tipo de crédito."
    )
    status_id: Optional[UUID] = PydanticField(
        None, description="Nuevo ID del estado de la solicitud."
    )
    approved_amount: Optional[float] = PydanticField(
        None, ge=0, description="Monto final aprobado."
    )
    approved_at: Optional[datetime] = PydanticField(
        None, description="Fecha de aprobación."
    )
    analyst_id: Optional[UUID] = PydanticField(
        None, description="ID del analista responsable."
    )
    rejection_reason: Optional[str] = PydanticField(
        None, max_length=500, description="Nueva razón de rechazo."
    )
    risk_score: Optional[float] = PydanticField(
        None, ge=0, le=1, description="Nueva puntuación de riesgo."
    )

    class Config:
        from_attributes = True


class RequestResponse(BaseRequestSchema):
    id: UUID = PydanticField(..., description="ID único de la solicitud.")
    credit_type: CreditType = PydanticField(
        ..., description="Detalles del tipo de crédito."
    )
    status: RequestStatus = PydanticField(
        ..., description="Detalles del estado de la solicitud."
    )
    approved_amount: Optional[float] = PydanticField(
        None, ge=0, description="Monto final aprobado."
    )
    approved_at: Optional[datetime] = PydanticField(
        None, description="Fecha de aprobación."
    )
    analyst_id: Optional[UUID] = PydanticField(
        None, description="ID del analista que aprobó o rechazó."
    )
    rejection_reason: Optional[str] = PydanticField(
        None, max_length=500, description="Razón si la solicitud fue rechazada."
    )
    risk_score: Optional[float] = PydanticField(
        None, ge=0, le=1, description="Puntuación de riesgo del cliente."
    )
    created_at: datetime = PydanticField(
        ..., description="Fecha de creación de la solicitud."
    )
    updated_at: datetime = PydanticField(
        ..., description="Última fecha de actualización de la solicitud."
    )

    class Config:
        from_attributes = True
