# flake8: noqa: F821
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from sqlmodel import Field, Relationship, SQLModel


class ClientProfileBase(SQLModel):
    user_id: UUID = Field(primary_key=True, index=True)
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
    address_line1: Optional[str] = None
    address_city: Optional[str] = None
    address_region: Optional[str] = None
    address_postal_code: Optional[str] = None
    annual_income: Optional[float] = Field(default=None, ge=0)
    years_of_agricultural_experience: Optional[int] = Field(default=None, ge=0)
    has_agricultural_insurance: Optional[bool] = Field(default=False)
    internal_credit_history_score: Optional[float] = Field(default=None, ge=0, le=1000)
    current_debt_to_income_ratio: Optional[float] = Field(default=None, ge=0)
    farm_size_hectares: Optional[float] = Field(default=None, ge=0)


class ClientProfile(ClientProfileBase, table=True):
    __tablename__ = "client_profiles"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    requests: List["Request"] = Relationship(back_populates="client_profile")
    notifications_users: List["NotificationsUser"] = Relationship(
        back_populates="client_profile"
    )
