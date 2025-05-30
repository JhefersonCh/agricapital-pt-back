from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RequestInterface:
    id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    requested_amount: Optional[float] = None
    term_months: Optional[int] = None
    annual_interest_rate: Optional[float] = None
    credit_type_id: Optional[UUID] = None
    status_id: Optional[UUID] = None
    approved_amount: Optional[float] = None
    approved_at: Optional[datetime] = None
    analyst_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    risk_score: Optional[float] = None
    risk_assessment_details: Optional[dict] = None
    purpose_description: Optional[str] = None
    applicant_contribution_amount: Optional[float] = None
    collateral_offered_description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
