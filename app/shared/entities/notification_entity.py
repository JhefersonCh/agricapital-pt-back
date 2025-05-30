# flake8: noqa: F821
from typing import List
from uuid import UUID
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class NotificationBase(SQLModel):
    id: UUID = Field(primary_key=True, index=True)
    title: str = Field(nullable=False)
    message: str = Field(nullable=False)


class Notification(NotificationBase, table=True):
    __tablename__ = "notifications"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notifications_users: List["NotificationsUser"] = Relationship(
        back_populates="notification"
    )
