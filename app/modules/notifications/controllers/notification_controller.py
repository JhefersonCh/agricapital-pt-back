from datetime import datetime
from uuid import UUID
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.modules.clients.services.client_service import ClientProfileNotFoundError
from app.modules.notifications.services.notification_service import (
    NotificationService,
)
from app.shared.guards.jwtGuard import jwt_guard
from fastapi import HTTPException, status

notificationRouter = APIRouter(
    prefix="/notifications",
    tags=["Notificaciones"],
    dependencies=[Depends(jwt_guard)],
)


@notificationRouter.get("/")
def get_notifications(
    db: Session = Depends(get_session), user_id: UUID = Depends(jwt_guard)
):
    try:
        notifications = NotificationService(db).get_notifications_by_user_id(user_id)
        return {"data": notifications}
    except ClientProfileNotFoundError:
        return {"data": []}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@notificationRouter.patch("/view/{notification_id}")
def view_notification(notification_id: UUID, db: Session = Depends(get_session)):
    try:
        notification = NotificationService(db).get_notification_by_id(notification_id)
        if notification is None:
            return None
        notification.read_at = datetime.now()
        db.commit()
        return notification
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
