from dataclasses import asdict
from typing import Optional
from uuid import UUID
from sqlmodel import select, Session
from app.modules.notifications.models.notification_model import (
    NotificationInterface,
    NotificationUserInterface,
)
from app.shared.entities.notification_entity import Notification
from app.shared.entities.notifications_user_entity import NotificationsUser
from app.modules.clients.services.client_service import ClientProfileService


class NotificationNotFoundError(Exception):
    def __init__(self):
        super().__init__("Notificación no encontrada")


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.client_service = ClientProfileService(db)

    def get_notifications_by_user_id(self, user_id: UUID) -> list[NotificationsUser]:
        client_profile = self.client_service.get_client_profile_by_user_id(user_id)
        if not client_profile:
            return []

        statement = (
            select(NotificationsUser, Notification)
            .join(Notification, NotificationsUser.notification_id == Notification.id)
            .where(NotificationsUser.user_id == user_id)
        )
        notifications = self.db.exec(statement).all()
        return [
            NotificationUserInterface(
                id=nu.id,
                notification_id=nu.notification_id,
                user_id=nu.user_id,
                created_at=nu.created_at,
                updated_at=nu.updated_at,
                read_at=nu.read_at,
                notification=NotificationInterface(
                    id=n.id,
                    title=n.title,
                    message=n.message,
                    created_at=n.created_at,
                    updated_at=n.updated_at,
                ),
            )
            for nu, n in notifications
        ]

    def create_notification_user(
        self, notification_user_data: NotificationUserInterface
    ) -> NotificationsUser:
        data_dict = asdict(notification_user_data)
        filtered_data = {k: v for k, v in data_dict.items() if v is not None}
        db_notification_user = NotificationsUser(**filtered_data)
        self.db.add(db_notification_user)
        self.db.commit()
        self.db.refresh(db_notification_user)
        return db_notification_user

    def get_notification_by_id(self, notification_id: UUID) -> Optional[NotificationUserInterface]:
        statement = (
            select(NotificationsUser, Notification)
            .join(Notification, NotificationsUser.notification_id == Notification.id)
            .where(NotificationsUser.id == notification_id)
        )
        
        result = self.db.exec(statement).first()

        if not result:
            return None

        nu, n = result
        
        return NotificationUserInterface(
            id=nu.id,
            notification_id=nu.notification_id,
            user_id=nu.user_id,
            created_at=nu.created_at,
            updated_at=nu.updated_at,
            read_at=nu.read_at,
            notification=NotificationInterface(
                id=n.id,
                title=n.title,
                message=n.message,
                created_at=n.created_at,
                updated_at=n.updated_at,
            ),
        )
