from typing import List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.requests.models.related_data_model import (
    CreditTypeInterface,
    RequestStatusInterface,
)
from app.shared.entities.credit_type_enity import CreditType
from app.shared.entities.request_status_entity import RequestStatus


class RequestRelatedData:
    def __init__(self, db: Session):
        self.db = db

    def get_credit_type(self, credit_type_id: UUID) -> CreditType:
        credit_type = (
            self.db.query(CreditType).filter(CreditType.id == credit_type_id).first()
        )
        if not credit_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit Type ID '{credit_type_id}' no encontrado.",
            )
        return credit_type

    def get_credit_type_by_params(
        self, params: CreditTypeInterface, with_error: bool = True
    ) -> CreditType:
        filters = [
            getattr(CreditType, field) == value
            for field, value in vars(params).items()
            if value is not None and hasattr(CreditType, field)
        ]
        credit_type = self.db.query(CreditType).filter(*filters).first()
        if not credit_type and with_error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit Type no encontrado.",
            )
        return credit_type

    def get_request_status_by_params(
        self, params: RequestStatusInterface, with_error: bool = True
    ) -> RequestStatus:
        filters = [
            getattr(RequestStatus, field) == value
            for field, value in vars(params).items()
            if value is not None and hasattr(RequestStatus, field)
        ]
        request_status = self.db.query(RequestStatus).filter(*filters).first()
        if not request_status and with_error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request Status no encontrado.",
            )
        return request_status

    def get_all_request_status(self) -> List[RequestStatus]:
        return self.db.query(RequestStatus).all()

    def get_all_credit_types(self) -> List[CreditType]:
        return self.db.query(CreditType).all()

    def get_related_data(self) -> Tuple[List[CreditType], List[RequestStatus]]:
        credit_types = self.get_all_credit_types()
        request_statuses = self.get_all_request_status()
        return credit_types, request_statuses

    def get_request_status(self, request_status_id: UUID) -> RequestStatus:
        request_status = self.db.get(RequestStatus, request_status_id)
        if not request_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request Status ID '{request_status_id}' no encontrado.",
            )
        return request_status
