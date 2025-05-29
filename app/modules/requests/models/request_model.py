from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RequestInterface:
    id: Optional[int] = None
    client_id: Optional[int] = None
    requested_amount: Optional[float] = None
    term_months: Optional[int] = None
    annual_interest_rate: Optional[float] = None
    credit_type_id: Optional[int] = None
    status_id: Optional[int] = None
    approved_amount: Optional[float] = None
    approved_at: Optional[datetime] = None
    analyst_id: Optional[int] = None
    rejection_reason: Optional[str] = None
    risk_score: Optional[float] = None
