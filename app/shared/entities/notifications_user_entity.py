from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from app.shared.entities.client_profile_entity import ClientProfile
from app.shared.entities.notification_entity import Notification


class NotificationsUserBase(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="ID único de la notificación.",
    )
    notification_id: UUID = Field(
        index=True, nullable=False, foreign_key="notifications.id"
    )
    user_id: UUID = Field(
        index=True, nullable=False, foreign_key="client_profiles.user_id"
    )
    read_at: Optional[datetime] = None


class NotificationsUser(NotificationsUserBase, table=True):
    __tablename__ = "notifications_users"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notification: Optional[Notification] = Relationship(
        back_populates="notifications_users"
    )
    client_profile: Optional[ClientProfile] = Relationship(
        back_populates="notifications_users"
    )
