from typing import Optional
from dataclasses import dataclass


@dataclass
class CreditTypeInterface:
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None


@dataclass
class RequestStatusInterface:
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
