import pytest
from unittest.mock import MagicMock, patch, ANY
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from datetime import timedelta
from dataclasses import asdict
from sqlmodel import Session
from sqlmodel.sql.expression import Select
from app.modules.notifications.services.notification_service import (
    NotificationService,
)
from app.modules.notifications.models.notification_model import (
    NotificationUserInterface,
)
from app.modules.clients.services.client_service import ClientProfileService

class MockClientProfile:
    def __init__(self, id: UUID, user_id: UUID):
        self.id = id
        self.user_id = user_id

class MockNotification:
    def __init__(self, id: UUID, title: str, message: str, created_at: datetime, updated_at: datetime):
        self.id = id
        self.title = title
        self.message = message
        self.created_at = created_at
        self.updated_at = updated_at

    def __eq__(self, other):
        if not isinstance(other, MockNotification):
            return NotImplemented
        return (self.id == other.id and self.title == other.title and
                self.message == other.message and self.created_at == other.created_at and
                self.updated_at == other.updated_at)

class MockNotificationsUser:
    def __init__(self, id: UUID, notification_id: UUID, user_id: UUID, created_at: datetime, updated_at: datetime, read_at: Optional[datetime] = None):
        self.id = id
        self.notification_id = notification_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.read_at = read_at

    def __eq__(self, other):
        if not isinstance(other, MockNotificationsUser):
            return NotImplemented
        return (self.id == other.id and self.notification_id == other.notification_id and
                self.user_id == other.user_id and self.created_at == other.created_at and
                self.updated_at == other.updated_at and self.read_at == other.read_at)


TEST_USER_ID = UUID("e952b630-3226-4364-b367-db273281c5f4")
TEST_NOTIFICATION_ID_1 = UUID("c7a8d9e4-6d0e-5f7a-9c2d-3456789abcde")
TEST_NOTIFICATION_USER_ID_1 = UUID("858a98fc-adc5-40b3-983e-8d4a1b4489e3")
TEST_NOTIFICATION_ID_2 = UUID("b2d9f7c3-5c9d-4e6f-8a1b-23456789abcd")
TEST_NOTIFICATION_USER_ID_2 = UUID("0207a401-2cb4-40d4-b3c7-8a8168f41430")
NON_EXISTENT_ID = uuid4()

NOW = datetime.now(timezone.utc)
ONE_HOUR_AGO = NOW - timedelta(hours=1)
TWO_HOURS_AGO = NOW - timedelta(hours=2)

@pytest.fixture
def mock_db_session():
    """Provee una sesión de base de datos mockeada para SQLModel."""
    return MagicMock(spec=Session)

@pytest.fixture
def mock_client_service():
    """Provee un ClientProfileService mockeado."""
    return MagicMock(spec=ClientProfileService)

@pytest.fixture
def notification_service(mock_db_session, mock_client_service):
    """Provee una instancia de NotificationService con dependencias mockeadas."""
    with patch('app.modules.notifications.services.notification_service.ClientProfileService', return_value=mock_client_service):
        service = NotificationService(db=mock_db_session)
        service.client_service = mock_client_service
        return service

def test_notification_service_init(mock_db_session):
    """
    Testea que NotificationService se inicializa correctamente y ClientProfileService es instanciado.
    """
    with patch('app.modules.notifications.services.notification_service.ClientProfileService') as MockClientProfileService:
        service = NotificationService(db=mock_db_session)
        MockClientProfileService.assert_called_once_with(mock_db_session)
        assert service.db == mock_db_session
        assert service.client_service == MockClientProfileService.return_value

def test_get_notifications_by_user_id_no_client_profile(notification_service, mock_client_service):
    """
    Testea que retorna una lista vacía si el usuario no tiene perfil de cliente.
    """
    mock_client_service.get_client_profile_by_user_id.return_value = None
    result = notification_service.get_notifications_by_user_id(TEST_USER_ID)
    assert result == []
    mock_client_service.get_client_profile_by_user_id.assert_called_once_with(TEST_USER_ID)

def test_get_notifications_by_user_id_no_notifications_found(notification_service, mock_client_service, mock_db_session):
    """
    Testea que retorna una lista vacía si no se encuentran notificaciones para el usuario.
    """
    mock_client_service.get_client_profile_by_user_id.return_value = MockClientProfile(id=uuid4(), user_id=TEST_USER_ID)
    mock_db_session.exec.return_value.all.return_value = []

    result = notification_service.get_notifications_by_user_id(TEST_USER_ID)

    assert result == []
    mock_client_service.get_client_profile_by_user_id.assert_called_once_with(TEST_USER_ID)
    mock_db_session.exec.assert_called_once()


def test_get_notifications_by_user_id_notifications_found(notification_service, mock_client_service, mock_db_session):
    """
    Testea que retorna las notificaciones correctas cuando se encuentran.
    """
    mock_client_profile = MockClientProfile(id=uuid4(), user_id=TEST_USER_ID)
    mock_client_service.get_client_profile_by_user_id.return_value = mock_client_profile

    mock_notification_1 = MockNotification(
        id=TEST_NOTIFICATION_ID_1, title="Bienvenida", message="Bienvenido a la app", created_at=TWO_HOURS_AGO, updated_at=TWO_HOURS_AGO
    )
    mock_notification_user_1 = MockNotificationsUser(
        id=TEST_NOTIFICATION_USER_ID_1, notification_id=TEST_NOTIFICATION_ID_1, user_id=TEST_USER_ID,
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO, read_at=None
    )

    mock_notification_2 = MockNotification(
        id=TEST_NOTIFICATION_ID_2, title="Actualización", message="Nueva versión disponible", created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO
    )
    mock_notification_user_2 = MockNotificationsUser(
        id=TEST_NOTIFICATION_USER_ID_2, notification_id=TEST_NOTIFICATION_ID_2, user_id=TEST_USER_ID,
        created_at=NOW, updated_at=NOW, read_at=NOW
    )

    mock_db_session.exec.return_value.all.return_value = [
        (mock_notification_user_1, mock_notification_1),
        (mock_notification_user_2, mock_notification_2),
    ]

    result = notification_service.get_notifications_by_user_id(TEST_USER_ID)

    assert len(result) == 2
    assert isinstance(result[0], NotificationUserInterface)
    assert result[0].id == TEST_NOTIFICATION_USER_ID_1
    assert result[0].notification.title == "Bienvenida"
    assert result[0].read_at is None

    assert result[1].id == TEST_NOTIFICATION_USER_ID_2
    assert result[1].notification.title == "Actualización"
    assert result[1].read_at == NOW

    mock_client_service.get_client_profile_by_user_id.assert_called_once_with(TEST_USER_ID)
    mock_db_session.exec.assert_called_once_with(ANY)

def test_create_notification_user_success(notification_service, mock_db_session):
    """
    Testea que create_notification_user crea y retorna una nueva notificación de usuario.
    """
    notification_user_data = NotificationUserInterface(
        id=TEST_NOTIFICATION_USER_ID_1,
        notification_id=TEST_NOTIFICATION_ID_1,
        user_id=TEST_USER_ID,
        created_at=NOW,
        updated_at=NOW,
        read_at=None,
    )

    mock_db_notification_user = MockNotificationsUser(
        id=TEST_NOTIFICATION_USER_ID_1,
        notification_id=TEST_NOTIFICATION_ID_1,
        user_id=TEST_USER_ID,
        created_at=NOW,
        updated_at=NOW,
        read_at=None
    )
    with patch('app.modules.notifications.services.notification_service.NotificationsUser', return_value=mock_db_notification_user) as MockNotificationsUserConstructor:
        result = notification_service.create_notification_user(notification_user_data)

        expected_kwargs = asdict(notification_user_data)
        expected_kwargs = {k: v for k, v in expected_kwargs.items() if v is not None}
        if 'notification' in expected_kwargs:
            del expected_kwargs['notification']

        MockNotificationsUserConstructor.assert_called_once_with(**expected_kwargs)
        mock_db_session.add.assert_called_once_with(mock_db_notification_user)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_db_notification_user)
        assert result == mock_db_notification_user

def test_get_notification_by_id_found(notification_service, mock_db_session):
    """
    Testea que retorna una notificación de usuario por su ID cuando se encuentra.
    """
    mock_notification = MockNotification(
        id=TEST_NOTIFICATION_ID_1, title="Título Notif", message="Mensaje Notif", created_at=TWO_HOURS_AGO, updated_at=TWO_HOURS_AGO
    )
    mock_notification_user = MockNotificationsUser(
        id=TEST_NOTIFICATION_USER_ID_1, notification_id=TEST_NOTIFICATION_ID_1, user_id=TEST_USER_ID,
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO, read_at=None
    )

    mock_db_session.exec.return_value.first.return_value = (mock_notification_user, mock_notification)

    result = notification_service.get_notification_by_id(TEST_NOTIFICATION_USER_ID_1)

    assert isinstance(result, NotificationUserInterface)
    assert result.id == TEST_NOTIFICATION_USER_ID_1
    assert result.notification_id == TEST_NOTIFICATION_ID_1
    assert result.user_id == TEST_USER_ID
    assert result.notification.title == "Título Notif"
    assert result.notification.message == "Mensaje Notif"
    mock_db_session.exec.assert_called_once_with(ANY)

def test_get_notification_by_id_not_found(notification_service, mock_db_session):
    """
    Testea que retorna None si la notificación de usuario no se encuentra por su ID.
    """
    mock_db_session.exec.return_value.first.return_value = None

    result = notification_service.get_notification_by_id(NON_EXISTENT_ID)

    assert result is None
    mock_db_session.exec.assert_called_once_with(ANY)
