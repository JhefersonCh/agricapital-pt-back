import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime
from app.modules.requests.dtos.crud_request_dto import RequestUpdate
from app.modules.requests.services.request_service import RequestService, InvalidReferenceIdError
from app.shared.entities.requestEntity import Request
from app.shared.entities.client_profile_entity import ClientProfile
from app.modules.requests.models.request_model import RequestInterface
from app.modules.clients.services.client_service import ClientProfileNotFoundError
from fastapi import HTTPException, status
from app.shared.entities.credit_type_enity import CreditType
from app.shared.entities.request_status_entity import RequestStatus


@pytest.fixture
def mock_db_session():
    mock = MagicMock()
    # Mock the .get() method of the session
    mock.get.side_effect = lambda entity, id: {
        UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"): MagicMock(id=UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"), name="Test Credit Type"),
        UUID("d4e5f6a7-b8c9-4902-def0-4567890123de"): MagicMock(id=UUID("d4e5f6a7-b8c9-4902-def0-4567890123de"), code="PENDING", description="Pending"),
        UUID("f6a7b8c9-d0e1-4904-f234-6789012345fa"): MagicMock(id=UUID("f6a7b8c9-d0e1-4904-f234-6789012345fa"), code="APPROVED", description="Approved"),
        UUID("d4e5f6a7-b8c9-4902-def0-4567890123de"): MagicMock(id=UUID("d4e5f6a7-b8c9-4902-def0-4567890123de"), code="PENDING", description="Pending"),
        UUID("f6a7b8c9-d0e1-4904-f234-6789012345fa"): MagicMock(id=UUID("f6a7b8c9-d0e1-4904-f234-6789012345fa"), code="APPROVED", description="Approved"),
        UUID("01a2b3c4-d5e6-4905-1234-789012345601"): MagicMock(id=UUID("01a2b3c4-d5e6-4905-1234-789012345601"), code="REJECTED", description="Rejected"),
    }.get(id) # This mock handles CreditType and RequestStatus for .get()

    # Mock the .exec().first() and .exec().all() for select statements
    mock_query_result = MagicMock()
    mock_query_result.first.return_value = None # Default for select.first()
    mock_query_result.all.return_value = [] # Default for select.all()
    mock.exec.return_value = mock_query_result

    return mock

@pytest.fixture
def mock_request_related_data():
    mock = MagicMock()
    mock.get_credit_type.return_value = MagicMock(id=UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"), name="Test Credit Type")
    mock.get_request_status.return_value = MagicMock(id=UUID("d4e5f6a7-b8c9-4902-def0-4567890123de"), code="PENDING", description="Pending")
    mock.get_request_status_by_params.return_value = MagicMock(id=UUID("f6a7b8c9-d0e1-4904-f234-6789012345fa"), code="APPROVED", description="Approved")
    return mock

@pytest.fixture
def mock_client_service():
    mock = MagicMock()
    mock.get_client_profile_by_user_id.return_value = ClientProfile(
        id=UUID("e952b630-3226-4364-b367-db273281c5f4"),
        user_id=UUID("e952b630-3226-4364-b367-db273281c5f4"),
        email="test@example.com",
        date_of_birth=datetime(1990, 1, 1).date(),
        annual_income=50000.0,
        years_of_agricultural_experience=5,
        has_agricultural_insurance=True,
        internal_credit_history_score=750,
        current_debt_to_income_ratio=0.3,
        farm_size_hectares=10.0
    )
    return mock

@pytest.fixture
def mock_notification_service():
    mock = MagicMock()
    mock_notification = MagicMock(
        id=UUID("a3f1e6d2-4b8c-4d5e-9b0f-123456789abc"),
        title="New Request",
        message="Your request has been submitted."
    )
    mock.create_notification_user.return_value = MagicMock(
        id=uuid4(),
        user_id=UUID("e952b630-3226-4364-b367-db273281c5f4"),
        notification_id=mock_notification.id,
        notification=mock_notification,
        read_at=None,
        created_at=datetime.now()
    )
    mock.get_notification_by_id.return_value = MagicMock(
        id=uuid4(),
        user_id=UUID("e952b630-3226-4364-b367-db273281c5f4"),
        notification_id=mock_notification.id,
        notification=mock_notification,
        read_at=None,
        created_at=datetime.now()
    )
    return mock

@pytest.fixture
def mock_mail_service():
    return MagicMock()

@pytest.fixture
def mock_ws_send_notification():
    return MagicMock()

@pytest.fixture
def request_service(mock_db_session, mock_request_related_data, mock_client_service,
                    mock_notification_service, mock_mail_service, mock_ws_send_notification):
    service = RequestService(
        db=mock_db_session,
        mail_service=mock_mail_service,
        ws_send_notification=mock_ws_send_notification
    )
    service.request_related_data = mock_request_related_data
    service.client_service = mock_client_service
    service.notification_service = mock_notification_service
    return service

# Mock the CreditRiskCalculator for all tests that call calculate_risk_score_from_request
@pytest.fixture(autouse=True)
def mock_credit_risk_calculator():
    with patch('app.modules.requests.services.request_service.CreditRiskCalculator') as MockCalculator:
        mock_instance = MockCalculator.return_value
        mock_instance.calculate_risk_score.return_value = MagicMock(
            risk_score=0.25,
            detailed_analysis={"category": "Low Risk", "details": "Good profile"},
            warning_flags=[]
        )
        yield MockCalculator


# --- Existing Unit Tests ---
def test_validate_reference_ids_success(request_service, mock_request_related_data):
    credit_type_id = UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab")
    status_id = UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")
    try:
        request_service._validate_reference_ids(credit_type_id, status_id)
        mock_request_related_data.get_credit_type.assert_called_once_with(credit_type_id)
        mock_request_related_data.get_request_status.assert_called_once_with(status_id)
    except InvalidReferenceIdError:
        pytest.fail("InvalidReferenceIdError was raised unexpectedly!")

def test_validate_reference_ids_invalid_credit_type(request_service, mock_request_related_data):
    credit_type_id = UUID("b2c3d4e5-f6a7-4890-bcde-2345678901bb")
    status_id = UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")
    mock_request_related_data.get_credit_type.side_effect = InvalidReferenceIdError("Invalid credit type")
    with pytest.raises(InvalidReferenceIdError, match="Invalid credit type"):
        request_service._validate_reference_ids(credit_type_id, status_id)

def test_calculate_risk_score_from_request(request_service, mock_client_service):
    client_id = UUID("e952b630-3226-4364-b367-db273281c5f4")
    client_profile = mock_client_service.get_client_profile_by_user_id(client_id)
    request = RequestInterface(
        id=UUID("9ef4240e-da77-45e3-b4ec-ccb9d1828d3a"),
        client_id=client_id,
        requested_amount=10000.0,
        term_months=12,
        annual_interest_rate=0.08,
        applicant_contribution_amount=1000.0,
        collateral_value=5000.0,
        number_of_dependents=2,
        other_income_sources=12222, # Changed to string as per common usage
        previous_defaults=0,
        credit_type_id=UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"),
        status_id=UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")
    )

    # The patch is now a fixture, so no need for `with patch(...)` here
    risk_score, detailed_analysis, warning_flags = request_service.calculate_risk_score_from_request(request, client_profile)

    assert risk_score == 0.25
    assert detailed_analysis == {"category": "Low Risk", "details": "Good profile"}
    assert warning_flags == []

@pytest.mark.asyncio
async def test_create_request_client_not_found(request_service, mock_client_service):
    client_id = UUID("e952b630-3226-4364-b367-db273281c5f4")
    request_data = RequestInterface(
        client_id=client_id,
        credit_type_id=UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"),
        status_id=UUID("d4e5f6a7-b8c9-4902-def0-4567890123de"),
        requested_amount=1000.0,
        term_months=12,
        annual_interest_rate=0.05,
        applicant_contribution_amount=100.0,
        number_of_dependents=1,
        other_income_sources=123123,
        previous_defaults=0,
        collateral_value=500.0
    )
    mock_client_service.get_client_profile_by_user_id.return_value = None

    with pytest.raises(ClientProfileNotFoundError):
        await request_service.create_request(request_data)

    mock_client_service.get_client_profile_by_user_id.assert_called_once_with(client_id)
    request_service.mail_service.send_email.assert_not_called()
    request_service.ws_send_notification.assert_not_called()

@pytest.mark.asyncio
async def test_create_request_invalid_reference_id(request_service, mock_request_related_data):
    client_id = UUID("e952b630-3226-4364-b367-db273281c5f4")
    credit_type_id = uuid4()
    status_id = UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")

    request_data = RequestInterface(
        client_id=client_id,
        credit_type_id=credit_type_id,
        status_id=status_id,
        requested_amount=1000.0,
        term_months=12,
        annual_interest_rate=0.05,
        applicant_contribution_amount=100.0,
        number_of_dependents=1,
        other_income_sources=123123,
        previous_defaults=0,
        collateral_value=500.0
    )

    mock_request_related_data.get_credit_type.side_effect = InvalidReferenceIdError("Credit Type not found")

    with pytest.raises(InvalidReferenceIdError, match="Credit Type not found"):
        await request_service.create_request(request_data)

    mock_request_related_data.get_credit_type.assert_called_once_with(credit_type_id)
    request_service.mail_service.send_email.assert_not_called()
    request_service.ws_send_notification.assert_not_called()

@pytest.mark.asyncio
async def test_create_request_approved_status_not_found(request_service, mock_request_related_data, mock_db_session):
    client_id = UUID("e952b630-3226-4364-b367-db273281c5f4")
    credit_type_id = UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab")
    pending_status_id = UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")

    request_data = RequestInterface(
        client_id=client_id,
        credit_type_id=credit_type_id,
        status_id=pending_status_id,
        requested_amount=1000.0,
        term_months=12,
        annual_interest_rate=0.05,
        applicant_contribution_amount=100.0,
        number_of_dependents=1,
        other_income_sources=123123,
        previous_defaults=0,
        collateral_value=500.0
    )

    mock_request_related_data.get_request_status_by_params.return_value = None # Simulate APPROVED status not found
    mock_db_session.exec.return_value.first.return_value = None # No existing request

    with pytest.raises(ValueError, match="Estado 'APPROVED' no configurado en la base de datos de estados."):
        await request_service.create_request(request_data)

    mock_request_related_data.get_request_status_by_params.assert_called_once()
    request_service.mail_service.send_email.assert_not_called()
    request_service.ws_send_notification.assert_not_called()

def test_update_request_not_found(request_service, mock_db_session):
    request_id = uuid4()
    request_update_data = RequestUpdate(requested_amount=100.0)
    mock_db_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_service.update_request(request_id, request_update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"Solicitud con ID '{request_id}' no encontrada para actualizar." in exc_info.value.detail
    mock_db_session.get.assert_called_once_with(Request, request_id)
    mock_db_session.commit.assert_not_called()

def test_update_request_invalid_credit_type_id(request_service, mock_db_session):
    request_id = UUID("9ef4240e-da77-45e3-b4ec-ccb9d1828d3a")
    current_credit_type_id = UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab")
    invalid_credit_type_id = uuid4()

    db_request_mock = MagicMock(spec=Request)
    db_request_mock.id = request_id
    db_request_mock.credit_type_id = current_credit_type_id
    mock_db_session.get.side_effect = lambda entity, id: db_request_mock if id == request_id else None
    mock_db_session.get.return_value = db_request_mock # For the initial db_request retrieval
    mock_db_session.get.side_effect = lambda entity, id: {
        request_id: db_request_mock,
        invalid_credit_type_id: None, # Simulate invalid credit type not found
        current_credit_type_id: MagicMock(id=current_credit_type_id) # For the _validate_reference_ids if called
    }.get(id)


    request_update_data = RequestUpdate(credit_type_id=invalid_credit_type_id)

    with pytest.raises(InvalidReferenceIdError, match=f"Credit Type ID '{invalid_credit_type_id}' no encontrado."):
        request_service.update_request(request_id, request_update_data)

    mock_db_session.get.assert_any_call(Request, request_id)
    mock_db_session.get.assert_any_call(CreditType, invalid_credit_type_id)
    mock_db_session.commit.assert_not_called()

def test_update_request_invalid_status_id(request_service, mock_db_session):
    request_id = UUID("9ef4240e-da77-45e3-b4ec-ccb9d1828d3a")
    current_status_id = UUID("d4e5f6a7-b8c9-4902-def0-4567890123de")
    invalid_status_id = uuid4()

    db_request_mock = MagicMock(spec=Request)
    db_request_mock.id = request_id
    db_request_mock.status_id = current_status_id
    db_request_mock.credit_type_id = UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab") # Ensure credit type is valid if checked

    # Mock the behavior of db_session.get
    mock_db_session.get.side_effect = lambda entity, id: {
        request_id: db_request_mock,
        invalid_status_id: None, # Simulate invalid status not found
        current_status_id: MagicMock(id=current_status_id),
        UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"): MagicMock(id=UUID("a1b2c3d4-e5f6-4789-abcd-1234567890ab"))
    }.get(id)

    request_update_data = RequestUpdate(status_id=invalid_status_id)

    with pytest.raises(InvalidReferenceIdError, match=f"Status ID '{invalid_status_id}' no encontrado."):
        request_service.update_request(request_id, request_update_data)

    mock_db_session.get.assert_any_call(Request, request_id)
    mock_db_session.get.assert_any_call(RequestStatus, invalid_status_id)
    mock_db_session.commit.assert_not_called()

# --- New Unit Tests for approve_request ---

@pytest.mark.asyncio
async def test_approve_request_not_found(request_service, mock_db_session):
    request_id = uuid4()
    analyst_id = UUID("64a1bc27-c4f4-474c-8cde-16a8fd96ba97")
    mock_db_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await request_service.approve_request(request_id, analyst_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"Solicitud con ID '{request_id}' no encontrada para aprobar." in exc_info.value.detail
    mock_db_session.get.assert_called_once_with(Request, request_id)
    mock_db_session.commit.assert_not_called()
    request_service.mail_service.send_email.assert_not_called()
    request_service.ws_send_notification.assert_not_called()


# --- New Unit Tests for reject_request ---
@pytest.mark.asyncio
async def test_reject_request_not_found(request_service, mock_db_session):
    request_id = uuid4()
    analyst_id = UUID("64a1bc27-c4f4-474c-8cde-16a8fd96ba97")
    mock_db_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await request_service.reject_request(request_id, analyst_id, "Some reason")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"Solicitud con ID '{request_id}' no encontrada para rechazar." in exc_info.value.detail
    mock_db_session.get.assert_called_once_with(Request, request_id)
    mock_db_session.commit.assert_not_called()
    request_service.mail_service.send_email.assert_not_called()
    request_service.ws_send_notification.assert_not_called()


def test_get_request_by_id_not_found(request_service, mock_db_session):
    request_id = uuid4()
    mock_db_session.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_service.get_request_by_id(request_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"Solicitud con ID '{request_id}' no encontrada." in exc_info.value.detail
    mock_db_session.exec.assert_called_once()

def test_get_request_by_client_id_not_found(request_service, mock_db_session):
    client_id = uuid4()
    mock_db_session.exec.return_value.first.return_value = None

    request_response = request_service.get_request_by_client_id(client_id)

    assert request_response is None
    mock_db_session.exec.assert_called_once()

# --- New Unit Tests for change_status ---
def test_change_status_not_found(request_service, mock_db_session):
    request_id = uuid4()
    new_status_id = UUID("e5f6a7b8-c9d0-4903-ef12-5678901234ef")
    mock_db_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        request_service.change_status(request_id, new_status_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"Solicitud con ID '{request_id}' no encontrada para cambiar el estado." in exc_info.value.detail
    mock_db_session.get.assert_called_once_with(Request, request_id)
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_get_paginated_list_with_invalid_order_by(request_service):
    with pytest.raises(HTTPException) as exc_info:
        await request_service.get_paginated_list(order_by="invalid_field")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ordenamiento por campo 'invalid_field' no permitido." in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_paginated_list_with_invalid_sort_order(request_service):
    with pytest.raises(HTTPException) as exc_info:
        await request_service.get_paginated_list(sort_order="sideways")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ordenamiento por orden 'sideways' no permitido." in exc_info.value.detail