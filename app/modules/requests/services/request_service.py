from datetime import datetime
from typing import Callable, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from fastapi_mail import MessageSchema
from sqlalchemy.orm import selectinload
from sqlmodel import Session, asc, desc, func, select
from app.modules.clients.services.client_service import (
    ClientProfileNotFoundError,
    ClientProfileService,
)

from app.modules.mails.services.mail_service import MailService
from app.modules.mails.services.template_service import TemplateService
from app.modules.notifications.models.notification_model import (
    NotificationUserInterface,
)
from app.modules.notifications.services.notification_service import NotificationService
from app.modules.requests.models.related_data_model import (
    RequestStatusInterface,
)
from app.modules.requests.models.request_model import RequestInterface
from app.modules.requests.services.calculate_risk_service import (
    CreditRequest,
    CreditRiskCalculator,
)
from app.modules.requests.services.request_related_data import RequestRelatedData
from app.shared.entities.client_profile_entity import ClientProfile
from app.shared.entities.credit_type_enity import CreditType
from app.modules.requests.dtos.crud_request_dto import RequestResponse, RequestUpdate
from app.shared.entities.requestEntity import Request
from app.shared.entities.request_status_entity import RequestStatus


class InvalidReferenceIdError(Exception):
    """Excepción lanzada cuando un ID de referencia (ej. status_id) no es válido."""

    pass


class RequestAlreadyApprovedError(Exception):
    """Excepción lanzada si ya existe una solicitud aprobada para el usuario."""

    pass


class RequestService:
    def __init__(
        self,
        db: Session,
        mail_service: Optional[MailService] = None,
        ws_send_notification: Optional[Callable] = None
    ):
        self.db = db
        self.request_related_data = RequestRelatedData(db)
        self.client_service = ClientProfileService(db)
        self.notification_service = NotificationService(db)
        self.mail_service = mail_service
        self.template_service = TemplateService()
        self.ws_send_notification = ws_send_notification

    def _validate_reference_ids(self, credit_type_id: UUID, status_id: UUID):
        self.request_related_data.get_credit_type(credit_type_id)
        self.request_related_data.get_request_status(status_id)

    async def create_request(
        self, request_create: RequestInterface
    ) -> Tuple[RequestResponse, bool]:
        client_profile = self.client_service.get_client_profile_by_user_id(
            request_create.client_id
        )
        if not client_profile:
            raise ClientProfileNotFoundError()
        try:
            self._validate_reference_ids(
                request_create.credit_type_id, request_create.status_id
            )
        except InvalidReferenceIdError as e:
            raise e

        approved_status = self.request_related_data.get_request_status_by_params(
            RequestStatusInterface(code="APPROVED")
        )
        user_with_request = self.get_request_by_client_id(request_create.client_id)

        if user_with_request:
            return self.update_request(user_with_request.id, request_create), False

        if not approved_status:
            raise ValueError(
                "Estado 'APPROVED' no configurado en la base de datos de estados."
            )

        db_request = Request(**request_create.dict())

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        self.update_request(db_request.id, request_create)
        notificationUser = self.notification_service.create_notification_user(
            NotificationUserInterface(
                user_id=request_create.client_id,
                notification_id="a3f1e6d2-4b8c-4d5e-9b0f-123456789abc",
            )
        )

        notificationId = notificationUser.id
        notificationUserCompleted = self.notification_service.get_notification_by_id(notificationId)

        if self.ws_send_notification and notificationUserCompleted and notificationUserCompleted.notification:
            notification_message = {
                "type": "new_notification",
                "notification_id": str(notificationUserCompleted.id),
                "title": notificationUserCompleted.notification.title,
                "message": notificationUserCompleted.notification.message,
                "read_at": notificationUserCompleted.read_at.isoformat() if notificationUserCompleted.read_at else None,
                "created_at": notificationUserCompleted.created_at.isoformat() if notificationUserCompleted.created_at else None,
                "user_id": str(notificationUserCompleted.user_id),
                "request_id": str(db_request.id),
                "status": "created",
            }
            await self.ws_send_notification(str(request_create.client_id), notification_message)
        if self.mail_service:
            await self.mail_service.send_email(
                MessageSchema(
                    subject="Solicitud de Crédito",
                    recipients=[client_profile.email],
                    body=self.template_service.request_sent(db_request),
                    subtype="html",
                )
            )

        return RequestResponse.model_validate(db_request), True

    def calculate_risk_score_from_request(
        self, request: Request, client_profile: ClientProfile
    ) -> float:
        credit_request = CreditRequest(
            date_of_birth=client_profile.date_of_birth,
            annual_income=client_profile.annual_income,
            years_of_agricultural_experience=client_profile.years_of_agricultural_experience,
            has_agricultural_insurance=client_profile.has_agricultural_insurance,
            internal_credit_history_score=client_profile.internal_credit_history_score,
            current_debt_to_income_ratio=client_profile.current_debt_to_income_ratio,
            farm_size_hectares=client_profile.farm_size_hectares,
            requested_amount=request.requested_amount,
            term_months=request.term_months,
            annual_interest_rate=request.annual_interest_rate,
            applicant_contribution_amount=request.applicant_contribution_amount,
            has_collateral=bool(request.collateral_value),
            collateral_value=request.collateral_value,
            number_of_dependents=request.number_of_dependents,
            other_income_sources=request.other_income_sources,
            previous_defaults=request.previous_defaults,
        )

        calculator = CreditRiskCalculator()
        result = calculator.calculate_risk_score(credit_request)
        return result.risk_score, result.detailed_analysis, result.warning_flags

    async def get_paginated_list(
        self,
        page: int = 1,
        client_id: Optional[UUID] = None,
        per_page: int = 10,
        status_id: Optional[UUID] = None,
        credit_type_id: Optional[UUID] = None,
        order_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "asc",
    ) -> Tuple[List[RequestResponse], int]:
        offset = (page - 1) * per_page
        limit = per_page
        count_statement = select(func.count(Request.id))
        data_statement = select(Request).options(
            selectinload(Request.credit_type), selectinload(Request.status)
        )

        if client_id:
            count_statement = count_statement.where(Request.client_id == client_id)
            data_statement = data_statement.where(Request.client_id == client_id)

        if status_id:
            status_obj = self.request_related_data.get_request_status(status_id)
            if status_obj:
                count_statement = count_statement.where(
                    Request.status_id == status_obj.id
                )
                data_statement = data_statement.where(
                    Request.status_id == status_obj.id
                )

        if credit_type_id:
            credit_type_obj = self.request_related_data.get_credit_type(credit_type_id)
            if credit_type_obj:
                count_statement = count_statement.where(
                    Request.credit_type_id == credit_type_obj.id
                )
                data_statement = data_statement.where(
                    Request.credit_type_id == credit_type_obj.id
                )

        total_items = self.db.exec(count_statement).first() or 0
        allowed_sort_fields = [
            "created_at",
            "updated_at",
            "requested_amount",
            "approved_amount",
            "term_months",
            "annual_interest_rate",
            "risk_score",
            "id",
        ]
        if order_by not in allowed_sort_fields and order_by is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ordenamiento por campo '{order_by}' no permitido.",
            )

        if sort_order not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ordenamiento por orden '{sort_order}' no permitido.",
            )

        if order_by and order_by in allowed_sort_fields:
            sort_column = getattr(Request, order_by)
            if sort_order and sort_order.lower() == "desc":
                data_statement = data_statement.order_by(desc(sort_column))
            elif sort_order and sort_order.lower() == "asc":
                data_statement = data_statement.order_by(asc(sort_column))
            else:
                data_statement = data_statement.order_by(desc(sort_column))
        else:
            data_statement = data_statement.order_by(desc(Request.created_at))

        data_statement = data_statement.offset(offset).limit(limit)
        requests = self.db.exec(data_statement).all()
        response_data = [RequestResponse.model_validate(req) for req in requests]
        return response_data, total_items

    def get_request_by_id(self, request_id: UUID) -> Optional[RequestResponse]:
        statement = select(Request).where(Request.id == request_id)

        db_request = self.db.exec(statement).first()
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con ID '{request_id}' no encontrada.",
            )

        return RequestResponse.model_validate(db_request)

    def get_all_requests(
        self, client_id: Optional[UUID] = None, offset: int = 0, limit: int = 100
    ) -> List[RequestResponse]:
        statement = select(Request)

        if client_id:
            statement = statement.where(Request.client_id == client_id)

        statement = statement.offset(offset).limit(limit)

        requests = self.db.exec(statement).all()

        return [RequestResponse.model_validate(req) for req in requests]

    def update_request(
        self, request_id: UUID, request_update: RequestUpdate
    ) -> RequestResponse:
        db_request = self.db.get(Request, request_id)
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con ID '{request_id}' no encontrada para actualizar.",
            )

        update_data = request_update.model_dump(exclude_unset=True)

        if (
            "credit_type_id" in update_data
            and update_data["credit_type_id"] != db_request.credit_type_id
        ):
            if not self.db.get(CreditType, update_data["credit_type_id"]):
                raise InvalidReferenceIdError(
                    f"Credit Type ID '{update_data['credit_type_id']}' no encontrado."
                )

        if (
            "status_id" in update_data
            and update_data["status_id"] != db_request.status_id
        ):
            if not self.db.get(RequestStatus, update_data["status_id"]):
                raise InvalidReferenceIdError(
                    f"Status ID '{update_data['status_id']}' no encontrado."
                )

        db_request.sqlmodel_update(update_data)
        db_request.updated_at = datetime.now()

        if (
            "status_id" in update_data
            and update_data["status_id"]
            == self.request_related_data.get_request_status_by_params(
                RequestStatusInterface(code="APPROVED")
            ).id
        ):
            db_request.approved_at = datetime.now()

        client_profile = self.client_service.get_client_profile_by_user_id(
            db_request.client_id
        )
        risk_score, risk_assessment_details, warning_flags = (
            self.calculate_risk_score_from_request(db_request, client_profile)
        )
        db_request.risk_score = risk_score
        db_request.risk_assessment_details = risk_assessment_details
        db_request.warning_flags = warning_flags

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        return RequestResponse.model_validate(db_request)

    def delete_request(self, request_id: UUID) -> bool:
        db_request = self.db.get(Request, request_id)
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con ID '{request_id}' no encontrada para eliminar.",
            )
        self.db.delete(db_request)
        self.db.commit()
        return True

    def get_request_by_client_id(self, client_id: UUID) -> Optional[RequestResponse]:

        db_request = self.db.exec(
            select(Request).filter(Request.client_id == client_id)
        ).first()
        if not db_request:
            return None
        return RequestResponse.model_validate(db_request)

    async def approve_request(
        self, request_id: UUID, user_id: UUID, approved_amount: Optional[float] = None
    ) -> RequestResponse:
        db_request = self.db.get(Request, request_id)
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con ID '{request_id}' no encontrada para aprobar.",
            )

        update_data = {
            "status_id": self.request_related_data.get_request_status_by_params(
                RequestStatusInterface(code="APPROVED")
            ).id
        }

        if approved_amount:
            update_data["approved_amount"] = approved_amount

        db_request.sqlmodel_update(update_data)
        db_request.updated_at = datetime.now()
        db_request.approved_at = datetime.now()
        db_request.analyst_id = user_id

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        notificationUser = self.notification_service.create_notification_user(
            NotificationUserInterface(
                user_id=db_request.client_id,
                notification_id="b2d9f7c3-5c9d-4e6f-8a1b-23456789abcd",
            )
        )
        notificationId = notificationUser.id
        notificationUserCompleted = self.notification_service.get_notification_by_id(notificationId)

        if self.ws_send_notification and notificationUserCompleted and notificationUserCompleted.notification:
            notification_message = {
                "type": "new_notification",
                "notification_id": str(notificationUserCompleted.id),
                "title": notificationUserCompleted.notification.title,
                "message": notificationUserCompleted.notification.message,
                "read_at": notificationUserCompleted.read_at.isoformat() if notificationUserCompleted.read_at else None,
                "created_at": notificationUserCompleted.created_at.isoformat() if notificationUserCompleted.created_at else None,
                "user_id": str(notificationUserCompleted.user_id),
                "request_id": str(db_request.id),
                "status": "approved",
            }
            await self.ws_send_notification(str(db_request.client_id), notification_message)

        if self.mail_service:
            await self.mail_service.send_email(
                MessageSchema(
                    subject="Solicitud Aprobada",
                    recipients=[db_request.client_profile.email],
                    body=self.template_service.request_approved(db_request),
                    subtype="html",
                )
            )

        return RequestResponse.model_validate(db_request)

    async def reject_request(
        self, request_id: UUID, user_id: UUID, rejection_reason: Optional[str] = None
    ) -> RequestResponse:
        db_request = self.db.get(Request, request_id)
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con ID '{request_id}' no encontrada para rechazar.",
            )

        update_data = {
            "status_id": self.request_related_data.get_request_status_by_params(
                RequestStatusInterface(code="REJECTED")
            ).id
        }

        if rejection_reason:
            update_data["rejection_reason"] = rejection_reason

        update_data["approved_amount"] = 0
        update_data["approved_at"] = None
        db_request.sqlmodel_update(update_data)
        db_request.updated_at = datetime.now()
        db_request.analyst_id = user_id

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        notificationUser = self.notification_service.create_notification_user(
            NotificationUserInterface(
                user_id=db_request.client_id,
                notification_id="c7a8d9e4-6d0e-5f7a-9c2d-3456789abcde",
            )
        )

        notificationId = notificationUser.id
        notificationUserCompleted = self.notification_service.get_notification_by_id(notificationId)
        if self.ws_send_notification and notificationUserCompleted and notificationUserCompleted.notification:
            notification_message = {
                "type": "new_notification",
                "notification_id": str(notificationUserCompleted.id),
                "title": notificationUserCompleted.notification.title,
                "message": notificationUserCompleted.notification.message,
                "read_at": notificationUserCompleted.read_at.isoformat() if notificationUserCompleted.read_at else None,
                "created_at": notificationUserCompleted.created_at.isoformat() if notificationUserCompleted.created_at else None,
                "user_id": str(notificationUserCompleted.user_id),
                "request_id": str(db_request.id),
                "status": "rejected",
            }
            await self.ws_send_notification(str(db_request.client_id), notification_message)

        if self.mail_service:
            await self.mail_service.send_email(
                MessageSchema(
                    subject="Solicitud Rechazada",
                    recipients=[db_request.client_profile.email],
                    body=self.template_service.request_rejected(
                        db_request,
                        "Estimado/a cliente",
                        rejection_reason=rejection_reason,
                    ),
                    subtype="html",
                )
            )

        return RequestResponse.model_validate(db_request)

    def change_status(self, request_id: UUID, status_id: UUID) -> RequestResponse:
        db_request = self.db.get(Request, request_id)
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Solicitud con ID '{request_id}' no encontrada para cambiar el estado.",
            )

        update_data = {
            "status_id": status_id,
            "approved_amount": 0,
            "approved_at": None,
            "rejection_reason": None,
        }
        db_request.sqlmodel_update(update_data)
        db_request.updated_at = datetime.now()

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        return RequestResponse.model_validate(db_request)
