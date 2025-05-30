from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class NotificationInterface:
    id: Optional[UUID] = None
    title: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class NotificationUserInterface:
    id: Optional[UUID] = None
    notification_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    notification: Optional[NotificationInterface] = None
