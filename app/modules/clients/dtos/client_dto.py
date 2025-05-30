from typing import Optional
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field as PydanticField


class ClientProfileCreate(BaseModel):
    user_id: UUID = PydanticField(
        description="ID único del usuario asociado a este perfil de cliente."
    )
    date_of_birth: Optional[date] = PydanticField(
        default=None, description="Fecha de nacimiento del cliente."
    )
    address_line1: Optional[str] = PydanticField(
        default=None,
        max_length=255,
        description="Primera línea de la dirección del cliente.",
    )
    address_city: Optional[str] = PydanticField(
        default=None, max_length=100, description="Ciudad de residencia del cliente."
    )
    address_region: Optional[str] = PydanticField(
        default=None,
        max_length=100,
        description="Región o departamento de residencia del cliente.",
    )
    address_postal_code: Optional[str] = PydanticField(
        default=None,
        max_length=20,
        description="Código postal de la dirección del cliente.",
    )
    annual_income: Optional[float] = PydanticField(
        default=None, ge=0, description="Ingreso anual estimado del cliente."
    )
    years_of_agricultural_experience: Optional[int] = PydanticField(
        default=None,
        ge=0,
        description="Años de experiencia del cliente en la actividad agrícola.",
    )
    has_agricultural_insurance: Optional[bool] = PydanticField(
        default=False, description="Indica si el cliente posee seguro agrícola."
    )
    internal_credit_history_score: Optional[float] = PydanticField(
        default=None,
        ge=0,
        le=1000,
        description="Puntuación interna del hist    orial crediticio del cliente (0-1000).",
    )
    current_debt_to_income_ratio: Optional[float] = PydanticField(
        default=None,
        ge=0,
        description="Relación actual de deuda sobre ingresos del cliente.",
    )
    farm_size_hectares: Optional[float] = PydanticField(
        default=None, ge=0, description="Tamaño de la finca del cliente en hectáreas."
    )


class ClientProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = PydanticField(
        default=None, description="Fecha de nacimiento del cliente."
    )
    address_line1: Optional[str] = PydanticField(
        default=None,
        max_length=255,
        description="Primera línea de la dirección del cliente.",
    )
    address_city: Optional[str] = PydanticField(
        default=None, max_length=100, description="Ciudad de residencia del cliente."
    )
    address_region: Optional[str] = PydanticField(
        default=None,
        max_length=100,
        description="Región o departamento de residencia del cliente.",
    )
    address_postal_code: Optional[str] = PydanticField(
        default=None,
        max_length=20,
        description="Código postal de la dirección del cliente.",
    )
    annual_income: Optional[float] = PydanticField(
        default=None, ge=0, description="Ingreso anual estimado del cliente."
    )
    years_of_agricultural_experience: Optional[int] = PydanticField(
        default=None,
        ge=0,
        description="Años de experiencia del cliente en la actividad agrícola.",
    )
    has_agricultural_insurance: Optional[bool] = PydanticField(
        default=None, description="Indica si el cliente posee seguro agrícola."
    )
    internal_credit_history_score: Optional[float] = PydanticField(
        default=None,
        ge=0,
        le=1000,
        description="Puntuación interna del historial crediticio del cliente (0-1000).",
    )
    current_debt_to_income_ratio: Optional[float] = PydanticField(
        default=None,
        ge=0,
        description="Relación actual de deuda sobre ingresos del cliente.",
    )
    farm_size_hectares: Optional[float] = PydanticField(
        default=None, ge=0, description="Tamaño de la finca del cliente en hectáreas."
    )


class ClientProfileResponse(ClientProfileCreate):
    user_id: UUID = PydanticField(
        description="ID único del usuario asociado a este perfil de cliente."
    )
    created_at: datetime = PydanticField(
        description="Fecha y hora de creación del perfil de cliente."
    )
    updated_at: datetime = PydanticField(
        description="Última fecha y hora de actualización del perfil de cliente."
    )
    email: Optional[str] = PydanticField(
        default=None, description="Correo electrónico del cliente."
    )

    class Config:
        from_attributes = True
