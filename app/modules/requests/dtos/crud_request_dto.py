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
        ..., example=12, gt=0, description="Plazo del crédito en meses."
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
    approved_amount: Optional[float] = PydanticField(
        None, example=950.0, ge=0, description="Monto final aprobado, si aplica."
    )
    approved_at: Optional[datetime] = PydanticField(
        None,
        example="2025-05-29T12:00:00Z",
        description="Fecha de aprobación de la solicitud.",
    )
    analyst_id: Optional[UUID] = PydanticField(
        None,
        example="d1e2f3a4-b5c6-7890-1234-567890abcdef",
        description="ID del analista que aprobó o rechazó.",
    )
    rejection_reason: Optional[str] = PydanticField(
        None,
        example="Falta de historial crediticio.",
        max_length=500,
        description="Razón si fue rechazada.",
    )
    risk_score: Optional[float] = PydanticField(
        None,
        example=73,
        ge=0,
        le=1000,
        description="Puntuación de riesgo del cliente (0-1000).",
    )
    risk_assessment_details: Optional[dict] = PydanticField(
        None,
        example={"score_details": {"income": 50, "debt": 20}},
        description="Detalle del análisis de riesgo.",
    )
    purpose_description: Optional[str] = PydanticField(
        None,
        example="Compra de fertilizantes.",
        max_length=1000,
        description="Descripción del propósito del crédito.",
    )
    applicant_contribution_amount: Optional[float] = PydanticField(
        0.0, example=100.0, ge=0, description="Aporte propio del solicitante."
    )
    collateral_offered_description: Optional[str] = PydanticField(
        None,
        example="Motocicleta como garantía.",
        max_length=1000,
        description="Garantía ofrecida por el solicitante.",
    )
    collateral_value: Optional[float] = PydanticField(
        None,
        example=500.0,
        ge=0,
        description="Valor de la garantía ofrecida, si aplica.",
    )
    number_of_dependents: Optional[int] = PydanticField(
        None, example=2, ge=0, description="Número de dependientes del solicitante."
    )
    other_income_sources: Optional[float] = PydanticField(
        None, example=100.0, ge=0, description="Otros ingresos del solicitante."
    )
    previous_defaults: Optional[int] = PydanticField(
        None,
        example=0,
        ge=0,
        description="Número de incumplimientos previos del solicitante.",
    )
    created_at: Optional[datetime] = PydanticField(
        None,
        example="2025-05-29T10:00:00Z",
        description="Fecha de creación de la solicitud.",
    )
    updated_at: Optional[datetime] = PydanticField(
        None,
        example="2025-05-29T10:05:00Z",
        description="Última fecha de actualización de la solicitud.",
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
        None, ge=0, le=1000, description="Nueva puntuación de riesgo."
    )
    risk_assessment_details: Optional[dict] = PydanticField(
        None, description="Detalle del análisis de riesgo."
    )
    collateral_value: Optional[float] = PydanticField(
        None,
        example=500.0,
        ge=0,
        description="Valor de la garantía ofrecida, si aplica.",
    )
    number_of_dependents: Optional[int] = PydanticField(
        None, example=2, ge=0, description="Número de dependientes del solicitante."
    )
    other_income_sources: Optional[float] = PydanticField(
        None, example=100.0, ge=0, description="Otros ingresos del solicitante."
    )
    previous_defaults: Optional[int] = PydanticField(
        None,
        example=0,
        ge=0,
        description="Número de incumplimientos previos del solicitante.",
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
        None, ge=0, le=1000, description="Puntuación de riesgo del cliente."
    )
    warning_flags: Optional[list[str]] = PydanticField(
        None, description="Banderas de advertencia si aplica."
    )
    created_at: datetime = PydanticField(
        ..., description="Fecha de creación de la solicitud."
    )
    updated_at: datetime = PydanticField(
        ..., description="Última fecha de actualización de la solicitud."
    )

    class Config:
        from_attributes = True


class RequestApprove(BaseModel):
    approved_amount: float = PydanticField(
        ..., ge=0, description="Monto final aprobado."
    )
    status_id: UUID = PydanticField(..., description="ID del estado de la solicitud.")


class RequestReject(BaseModel):
    rejection_reason: str = PydanticField(
        ..., max_length=500, description="Razón de rechazo."
    )
    status_id: UUID = PydanticField(..., description="ID del estado de la solicitud.")


class RequestChangeStatus(BaseModel):
    status_id: UUID = PydanticField(..., description="ID del estado de la solicitud.")
