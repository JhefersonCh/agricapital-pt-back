import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from fastapi import HTTPException, status
from app.modules.requests.services.request_related_data import RequestRelatedData
from app.shared.entities.credit_type_enity import CreditType
from app.shared.entities.request_status_entity import RequestStatus

# --- Fixtures ---

@pytest.fixture
def mock_db_session():
    """Provides a mock SQLAlchemy session."""
    return MagicMock()

@pytest.fixture
def request_related_data_service(mock_db_session):
    """Provides an instance of RequestRelatedData service with a mocked DB session."""
    return RequestRelatedData(db=mock_db_session)

# --- Mock Data and Classes ---

# Mock CreditTypeInterface for input parameters
class MockCreditTypeInterface:
    def __init__(self, id: UUID = None, name: str = None, code: str = None):
        self.id = id
        self.name = name
        self.code = code

# Mock RequestStatusInterface for input parameters
class MockRequestStatusInterface:
    def __init__(self, id: UUID = None, name: str = None, code: str = None):
        self.id = id
        self.name = name
        self.code = code

# Mock CreditType entity for database returns
class MockCreditType:
    def __init__(self, id: UUID, name: str, code: str):
        self.id = id
        self.name = name
        self.code = code

    def __eq__(self, other):
        if not isinstance(other, MockCreditType):
            return NotImplemented
        return self.id == other.id and self.name == other.name and self.code == other.code

# Mock RequestStatus entity for database returns
class MockRequestStatus:
    def __init__(self, id: UUID, name: str, code: str):
        self.id = id
        self.name = name
        self.code = code

    def __eq__(self, other):
        if not isinstance(other, MockRequestStatus):
            return NotImplemented
        return self.id == other.id and self.name == other.name and self.code == other.code

# Example UUIDs for testing
TEST_CREDIT_TYPE_ID_1 = UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab")
TEST_CREDIT_TYPE_ID_2 = UUID("b2c3d4e5-f6a7-4890-bcde-2345678901bc")
TEST_REQUEST_STATUS_ID_1 = UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")
TEST_REQUEST_STATUS_ID_2 = UUID("e5f6a7b8-c9d0-4903-ef12-5678901234ef")
NON_EXISTENT_ID = uuid4()



def test_get_credit_type_not_found(request_related_data_service, mock_db_session):
    """
    Test that get_credit_type raises HTTPException 404 when not found.
    """
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_related_data_service.get_credit_type(NON_EXISTENT_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert (
        exc_info.value.detail
        == f"Credit Type ID '{NON_EXISTENT_ID}' no encontrado."
    )
    mock_db_session.query.assert_called_once_with(CreditType)

# --- Tests for get_credit_type_by_params ---

def test_get_credit_type_by_params_found(request_related_data_service, mock_db_session):
    """
    Test that get_credit_type_by_params returns a CreditType when found by parameters.
    """
    mock_credit_type = MockCreditType(
        id=TEST_CREDIT_TYPE_ID_1, name="Personal", code="PRSNL"
    )
    mock_params = MockCreditTypeInterface(name="Personal", code="PRSNL")
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_credit_type

    result = request_related_data_service.get_credit_type_by_params(mock_params)

    assert result == mock_credit_type
    mock_db_session.query.assert_called_once_with(CreditType)
    # The filter arguments will be dynamic, so we check if filter was called
    assert mock_db_session.query.return_value.filter.called

def test_get_credit_type_by_params_not_found_with_error(
    request_related_data_service, mock_db_session
):
    """
    Test that get_credit_type_by_params raises HTTPException 404 when not found
    and with_error is True.
    """
    mock_params = MockCreditTypeInterface(name="NonExistent", code="NEX")
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_related_data_service.get_credit_type_by_params(mock_params, with_error=True)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Credit Type no encontrado."
    mock_db_session.query.assert_called_once_with(CreditType)

def test_get_credit_type_by_params_not_found_without_error(
    request_related_data_service, mock_db_session
):
    """
    Test that get_credit_type_by_params returns None when not found
    and with_error is False.
    """
    mock_params = MockCreditTypeInterface(name="NonExistent", code="NEX")
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = request_related_data_service.get_credit_type_by_params(mock_params, with_error=False)

    assert result is None
    mock_db_session.query.assert_called_once_with(CreditType)

def test_get_credit_type_by_params_with_partial_params(request_related_data_service, mock_db_session):
    """
    Test that get_credit_type_by_params works with only some parameters provided.
    """
    mock_credit_type = MockCreditType(
        id=TEST_CREDIT_TYPE_ID_1, name="Vehículo", code="VEH"
    )
    mock_params = MockCreditTypeInterface(name="Vehículo") # Only name provided
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_credit_type

    result = request_related_data_service.get_credit_type_by_params(mock_params)

    assert result == mock_credit_type
    mock_db_session.query.assert_called_once_with(CreditType)
    # The filter arguments will be dynamic, so we check if filter was called
    assert mock_db_session.query.return_value.filter.called


# --- Tests for get_request_status_by_params ---

def test_get_request_status_by_params_found(request_related_data_service, mock_db_session):
    """
    Test that get_request_status_by_params returns a RequestStatus when found by parameters.
    """
    mock_request_status = MockRequestStatus(
        id=TEST_REQUEST_STATUS_ID_1, name="Pendiente", code="PENDING"
    )
    mock_params = MockRequestStatusInterface(name="Pendiente", code="PENDING")
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_request_status

    result = request_related_data_service.get_request_status_by_params(mock_params)

    assert result == mock_request_status
    mock_db_session.query.assert_called_once_with(RequestStatus)
    assert mock_db_session.query.return_value.filter.called

def test_get_request_status_by_params_not_found_with_error(
    request_related_data_service, mock_db_session
):
    """
    Test that get_request_status_by_params raises HTTPException 404 when not found
    and with_error is True.
    """
    mock_params = MockRequestStatusInterface(name="NonExistent", code="NEX")
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_related_data_service.get_request_status_by_params(mock_params, with_error=True)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Request Status no encontrado."
    mock_db_session.query.assert_called_once_with(RequestStatus)

def test_get_request_status_by_params_not_found_without_error(
    request_related_data_service, mock_db_session
):
    """
    Test that get_request_status_by_params returns None when not found
    and with_error is False.
    """
    mock_params = MockRequestStatusInterface(name="NonExistent", code="NEX")
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = request_related_data_service.get_request_status_by_params(mock_params, with_error=False)

    assert result is None
    mock_db_session.query.assert_called_once_with(RequestStatus)

def test_get_request_status_by_params_with_partial_params(request_related_data_service, mock_db_session):
    """
    Test that get_request_status_by_params works with only some parameters provided.
    """
    mock_request_status = MockRequestStatus(
        id=TEST_REQUEST_STATUS_ID_1, name="Aprobado", code="APPROVED"
    )
    mock_params = MockRequestStatusInterface(code="APPROVED") # Only code provided
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_request_status

    result = request_related_data_service.get_request_status_by_params(mock_params)

    assert result == mock_request_status
    mock_db_session.query.assert_called_once_with(RequestStatus)
    assert mock_db_session.query.return_value.filter.called


# --- Tests for get_all_request_status ---

def test_get_all_request_status(request_related_data_service, mock_db_session):
    """
    Test that get_all_request_status returns a list of all request statuses.
    """
    mock_statuses = [
        MockRequestStatus(id=TEST_REQUEST_STATUS_ID_1, name="Pendiente", code="PENDING"),
        MockRequestStatus(id=TEST_REQUEST_STATUS_ID_2, name="Aprobado", code="APPROVED"),
    ]
    mock_db_session.query.return_value.all.return_value = mock_statuses

    result = request_related_data_service.get_all_request_status()

    assert result == mock_statuses
    mock_db_session.query.assert_called_once_with(RequestStatus)
    mock_db_session.query.return_value.all.assert_called_once()

# --- Tests for get_all_credit_types ---

def test_get_all_credit_types(request_related_data_service, mock_db_session):
    """
    Test that get_all_credit_types returns a list of all credit types.
    """
    mock_credit_types = [
        MockCreditType(id=TEST_CREDIT_TYPE_ID_1, name="Personal", code="PRSNL"),
        MockCreditType(id=TEST_CREDIT_TYPE_ID_2, name="Vehículo", code="VEH"),
    ]
    mock_db_session.query.return_value.all.return_value = mock_credit_types

    result = request_related_data_service.get_all_credit_types()

    assert result == mock_credit_types
    mock_db_session.query.assert_called_once_with(CreditType)
    mock_db_session.query.return_value.all.assert_called_once()

# --- Tests for get_related_data ---

def test_get_related_data(request_related_data_service, mock_db_session):
    """
    Test that get_related_data returns a tuple of lists containing
    all credit types and all request statuses.
    """
    mock_credit_types = [
        MockCreditType(id=TEST_CREDIT_TYPE_ID_1, name="Personal", code="PRSNL")
    ]
    mock_statuses = [
        MockRequestStatus(id=TEST_REQUEST_STATUS_ID_1, name="Pendiente", code="PENDING")
    ]

    # Mock the internal calls to get_all_credit_types and get_all_request_status
    # We use patch.object to mock methods on the service instance itself
    with patch.object(request_related_data_service, 'get_all_credit_types', return_value=mock_credit_types) as mock_get_credit_types, \
         patch.object(request_related_data_service, 'get_all_request_status', return_value=mock_statuses) as mock_get_request_status:

        result_credit_types, result_request_statuses = request_related_data_service.get_related_data()

        assert result_credit_types == mock_credit_types
        assert result_request_statuses == mock_statuses
        mock_get_credit_types.assert_called_once()
        mock_get_request_status.assert_called_once()

# --- Tests for get_request_status ---

def test_get_request_status_found(request_related_data_service, mock_db_session):
    """
    Test that get_request_status returns a RequestStatus when found using db.get.
    """
    mock_request_status = MockRequestStatus(
        id=TEST_REQUEST_STATUS_ID_1, name="Pendiente", code="PENDING"
    )
    # db.get is mocked directly on the session
    mock_db_session.get.return_value = mock_request_status

    result = request_related_data_service.get_request_status(TEST_REQUEST_STATUS_ID_1)

    assert result == mock_request_status
    mock_db_session.get.assert_called_once_with(RequestStatus, TEST_REQUEST_STATUS_ID_1)

def test_get_request_status_not_found(request_related_data_service, mock_db_session):
    """
    Test that get_request_status raises HTTPException 404 when not found using db.get.
    """
    mock_db_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_related_data_service.get_request_status(NON_EXISTENT_ID)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert (
        exc_info.value.detail
        == f"Request Status ID '{NON_EXISTENT_ID}' no encontrado."
    )
    mock_db_session.get.assert_called_once_with(RequestStatus, NON_EXISTENT_ID)

