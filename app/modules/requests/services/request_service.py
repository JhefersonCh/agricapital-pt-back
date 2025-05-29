from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, func, select
from app.modules.requests.models.related_data_model import (
    RequestStatusInterface,
)
from app.modules.requests.models.request_model import RequestInterface
from app.modules.requests.services.request_related_data import RequestRelatedData
from app.shared.entities.credit_type_enity import CreditType
from app.shared.entities.requestEntity import Request
from app.modules.requests.dtos.crud_request_dto import RequestResponse, RequestUpdate
from app.shared.entities.request_status_entity import RequestStatus


class InvalidReferenceIdError(Exception):
    """Excepción lanzada cuando un ID de referencia (ej. status_id) no es válido."""

    pass


class RequestAlreadyApprovedError(Exception):
    """Excepción lanzada si ya existe una solicitud aprobada para el usuario."""

    pass


class RequestService:
    def __init__(self, db: Session):
        self.db = db
        self.request_related_data = RequestRelatedData(db)

    def _validate_reference_ids(self, credit_type_id: UUID, status_id: UUID):
        self.request_related_data.get_credit_type(credit_type_id)
        self.request_related_data.get_request_status(status_id)

    def create_request(self, request_create: RequestInterface) -> RequestResponse:
        try:
            self._validate_reference_ids(
                request_create.credit_type_id, request_create.status_id
            )
        except InvalidReferenceIdError as e:
            raise e

        approved_status = self.request_related_data.get_request_status_by_params(
            RequestStatusInterface(code="APPROVED")
        )

        if not approved_status:
            raise ValueError(
                "Estado 'APPROVED' no configurado en la base de datos de estados."
            )

        db_request = Request(**request_create.dict())

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        return RequestResponse.model_validate(db_request)

    async def get_paginated_list(
        self,
        client_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 100,
        status_id: Optional[UUID] = None,
        credit_type_id: Optional[UUID] = None,
    ) -> Tuple[List[RequestResponse], int]:

        count_statement = select(func.count(Request.id))

        data_statement = select(Request)

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

        data_statement = data_statement.offset(offset).limit(limit)

        requests = self.db.exec(data_statement).all()
        return requests, total_items

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
