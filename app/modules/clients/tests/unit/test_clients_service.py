import pytest
from unittest.mock import MagicMock, patch, ANY
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlmodel import Session
from pydantic import BaseModel
from app.modules.clients.services.client_service import (
    ClientProfileService,
    ClientProfileNotFoundError,
)
from app.modules.clients.dtos.client_dto import (
    ClientProfileResponse,
)
from app.shared.entities.client_profile_entity import ClientProfile


# --- Mock Data and Classes ---
class MockClientProfile:
    def __init__(self, id: UUID, user_id: UUID, email: str, created_at: datetime, updated_at: datetime, **kwargs):
        self.id = id
        self.user_id = user_id
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at
        self._extra_attrs = kwargs

    def __getattr__(self, name):
        if name in self._extra_attrs:
            return self._extra_attrs[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __eq__(self, other):
        if not isinstance(other, MockClientProfile):
            return NotImplemented
        return (self.id == other.id and self.user_id == other.user_id and
                self.name == other.name and self.email == other.email and
                self.created_at == other.created_at and self.updated_at == other.updated_at)

    def sqlmodel_update(self, data: dict):
        """Simulates SQLModel's update method."""
        for key, value in data.items():
            setattr(self, key, value)

# Mock ClientInterface (Pydantic BaseModel for input)
class MockClientInterface(BaseModel):
    user_id: UUID
    email: str
    address: Optional[str] = None

    def dict(self, **kwargs):
        return self.model_dump(**kwargs)

# Mock ClientProfileResponse (Pydantic BaseModel for output)
class MockClientProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    email: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def model_validate(cls, obj: ANY):
        """Simulates Pydantic's model_validate for testing."""
        if isinstance(obj, MockClientProfile):
            return cls(
                id=obj.id,
                user_id=obj.user_id,
                email=obj.email,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
            )
        raise TypeError("Object is not a MockClientProfile instance")


# Mock ClientProfileUpdate (Pydantic BaseModel for update input)
class MockClientProfileUpdate(BaseModel):
    email: Optional[str] = None

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)


TEST_USER_ID = UUID("e952b630-3226-4364-b367-db273281c5f4")
TEST_CLIENT_PROFILE_ID = UUID("e952b630-3226-4364-b367-db273281c5f4")
NON_EXISTENT_USER_ID = uuid4()

NOW = datetime.now(timezone.utc)
ONE_HOUR_AGO = NOW - timedelta(hours=1)
TWO_HOURS_AGO = NOW - timedelta(hours=2)

# --- Fixtures ---

@pytest.fixture
def mock_db_session():
    """Provee una sesión de base de datos mockeada para SQLModel."""
    return MagicMock(spec=Session)

@pytest.fixture
def client_profile_service(mock_db_session):
    """Provee una instancia de ClientProfileService con una sesión de DB mockeada."""
    return ClientProfileService(db=mock_db_session)

# --- Tests para _client_exists ---

def test_client_exists_found(client_profile_service, mock_db_session):
    """
    Testea que _client_exists retorna True si el cliente existe.
    """
    mock_db_session.get.return_value = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, email="test@example.com",
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO
    )
    assert client_profile_service._client_exists(TEST_USER_ID) is not None
    mock_db_session.get.assert_called_once_with(ClientProfile, TEST_USER_ID)

def test_client_exists_not_found(client_profile_service, mock_db_session):
    """
    Testea que _client_exists retorna False si el cliente no existe.
    """
    mock_db_session.get.return_value = None
    assert client_profile_service._client_exists(NON_EXISTENT_USER_ID) is None
    mock_db_session.get.assert_called_once_with(ClientProfile, NON_EXISTENT_USER_ID)

@patch('app.modules.clients.services.client_service.datetime')
@patch.object(ClientProfileService, 'update_client_profile')
@patch.object(ClientProfileService, '_client_exists')
def test_create_client_profile_new_client(
    mock_client_exists, mock_update_profile, mock_datetime, client_profile_service, mock_db_session
):
    """
    Testea la creación de un nuevo perfil de cliente.
    """
    mock_client_exists.return_value = None
    mock_datetime.now.return_value = NOW

    profile_data = MockClientInterface(
        user_id=TEST_USER_ID, email="nuevo@example.com"
    )
    
    mock_db_profile = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID,
        user_id=TEST_USER_ID,
        email="nuevo@example.com",
        created_at=NOW,
        updated_at=NOW
    )
    with patch('app.modules.clients.services.client_service.ClientProfile', return_value=mock_db_profile) as MockClientProfileConstructor:
        result_profile, created = client_profile_service.create_client_profile(profile_data)

        mock_client_exists.assert_called_once_with(TEST_USER_ID)
        mock_update_profile.assert_not_called()
        MockClientProfileConstructor.assert_called_once_with(**profile_data.dict())
        mock_db_session.add.assert_called_once_with(mock_db_profile)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_db_profile)

        assert created is True
        assert isinstance(result_profile, ClientProfileResponse)
        assert result_profile.user_id == TEST_USER_ID
        assert result_profile.email == "nuevo@example.com"
        assert result_profile.created_at == NOW
        assert result_profile.updated_at == NOW


@patch('app.modules.clients.services.client_service.datetime')
@patch.object(ClientProfileService, 'update_client_profile')
@patch.object(ClientProfileService, '_client_exists')
def test_create_client_profile_existing_client(
    mock_client_exists, mock_update_profile, mock_datetime, client_profile_service, mock_db_session
):
    """
    Testea la actualización de un perfil existente si el cliente ya existe.
    """
    mock_client_exists.return_value = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, email="existing@example.com",
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO
    )
    
    profile_data = MockClientInterface(
        user_id=TEST_USER_ID, email="updated@example.com"
    )
    
    updated_response = ClientProfileResponse(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, email="updated@example.com",
        created_at=ONE_HOUR_AGO, updated_at=NOW
    )
    mock_update_profile.return_value = updated_response

    result_profile, created = client_profile_service.create_client_profile(profile_data)

    mock_client_exists.assert_called_once_with(TEST_USER_ID)
    mock_update_profile.assert_called_once_with(TEST_USER_ID, profile_data)
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()

    assert created is False
    assert result_profile == updated_response

# --- Tests para get_client_profile_by_user_id ---

@patch.object(ClientProfileResponse, 'model_validate')
def test_get_client_profile_by_user_id_found(mock_model_validate, client_profile_service, mock_db_session):
    """
    Testea que get_client_profile_by_user_id retorna el perfil cuando se encuentra.
    """
    mock_db_profile = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, name="Found Client", email="found@example.com",
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO
    )
    mock_db_session.get.return_value = mock_db_profile
    
    expected_response = ClientProfileResponse(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, name="Found Client", email="found@example.com",
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO
    )
    mock_model_validate.return_value = expected_response

    result = client_profile_service.get_client_profile_by_user_id(TEST_USER_ID)

    mock_db_session.get.assert_called_once_with(ClientProfile, TEST_USER_ID)
    mock_model_validate.assert_called_once_with(mock_db_profile)
    assert result == expected_response

def test_get_client_profile_by_user_id_not_found(client_profile_service, mock_db_session):
    """
    Testea que get_client_profile_by_user_id levanta ClientProfileNotFoundError si no se encuentra.
    """
    mock_db_session.get.return_value = None
    with pytest.raises(ClientProfileNotFoundError):
        client_profile_service.get_client_profile_by_user_id(NON_EXISTENT_USER_ID)
    mock_db_session.get.assert_called_once_with(ClientProfile, NON_EXISTENT_USER_ID)

# --- Tests para update_client_profile ---

@patch('app.modules.clients.services.client_service.datetime')
@patch.object(ClientProfileResponse, 'model_validate')
def test_update_client_profile_success(mock_model_validate, mock_datetime, client_profile_service, mock_db_session):
    """
    Testea la actualización exitosa de un perfil de cliente.
    """
    existing_profile = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, name="Old Name", email="old@example.com",
        created_at=TWO_HOURS_AGO, updated_at=TWO_HOURS_AGO
    )
    mock_db_session.get.return_value = existing_profile
    mock_datetime.now.return_value = NOW

    update_data = MockClientProfileUpdate(name="New Name", email="new@example.com")
    
    updated_db_profile = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, name="New Name", email="new@example.com",
        created_at=TWO_HOURS_AGO, updated_at=NOW
    )
    mock_model_validate.return_value = ClientProfileResponse(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, name="New Name", email="new@example.com",
        created_at=TWO_HOURS_AGO, updated_at=NOW
    )

    result = client_profile_service.update_client_profile(TEST_USER_ID, update_data)

    mock_db_session.get.assert_called_once_with(ClientProfile, TEST_USER_ID)
    assert existing_profile.email == "new@example.com"
    assert existing_profile.updated_at == NOW
    mock_db_session.add.assert_called_once_with(existing_profile)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(existing_profile)
    mock_model_validate.assert_called_once_with(existing_profile)
    assert isinstance(result, ClientProfileResponse)

def test_update_client_profile_not_found(client_profile_service, mock_db_session):
    """
    Testea que update_client_profile levanta ClientProfileNotFoundError si no se encuentra.
    """
    mock_db_session.get.return_value = None
    update_data = MockClientProfileUpdate(name="Non Existent")
    with pytest.raises(ClientProfileNotFoundError):
        client_profile_service.update_client_profile(NON_EXISTENT_USER_ID, update_data)
    mock_db_session.get.assert_called_once_with(ClientProfile, NON_EXISTENT_USER_ID)

def test_delete_client_profile_success(client_profile_service, mock_db_session):
    """
    Testea la eliminación exitosa de un perfil de cliente.
    """
    existing_profile = MockClientProfile(
        id=TEST_CLIENT_PROFILE_ID, user_id=TEST_USER_ID, name="To Delete", email="delete@example.com",
        created_at=ONE_HOUR_AGO, updated_at=ONE_HOUR_AGO
    )
    mock_db_session.get.return_value = existing_profile

    result = client_profile_service.delete_client_profile(TEST_USER_ID)

    mock_db_session.get.assert_called_once_with(ClientProfile, TEST_USER_ID)
    mock_db_session.delete.assert_called_once_with(existing_profile)
    mock_db_session.commit.assert_called_once()
    assert result is True

def test_delete_client_profile_not_found(client_profile_service, mock_db_session):
    """
    Testea que delete_client_profile levanta ClientProfileNotFoundError si no se encuentra.
    """
    mock_db_session.get.return_value = None
    with pytest.raises(ClientProfileNotFoundError):
        client_profile_service.delete_client_profile(NON_EXISTENT_USER_ID)
    mock_db_session.get.assert_called_once_with(ClientProfile, NON_EXISTENT_USER_ID)
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()
