from typing import Optional
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class ClientInterface:
    id: Optional[int] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    address_line1: Optional[str] = None
    address_city: Optional[str] = None
    address_region: Optional[str] = None
    address_postal_code: Optional[str] = None
    risk_score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
