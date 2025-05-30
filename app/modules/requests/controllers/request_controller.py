from typing import Optional
from uuid import UUID
from fastapi import Depends, APIRouter, Query
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.modules.mails.dependencies import get_mail_service
from app.modules.mails.services.mail_service import MailService
from app.modules.requests.dtos.crud_request_dto import (
    RequestApprove,
    RequestChangeStatus,
    RequestCreate,
    RequestReject,
    RequestUpdate,
)
from app.modules.requests.services.request_related_data import RequestRelatedData
from app.modules.requests.services.request_service import RequestService
from app.shared.dtos.pagination_dto import PaginatedRequestsResponse, PaginationMeta
from app.shared.guards.jwtGuard import jwt_guard
from fastapi import HTTPException, status

requestRouter = APIRouter(
    prefix="/requests",
    tags=["Solicitudes de crédito"],
    dependencies=[Depends(jwt_guard)],
)


@requestRouter.get("/related-data")
def get_related_data(db: Session = Depends(get_session)):
    try:
        credit_types, request_statuses = RequestRelatedData(db).get_related_data()
        return {
            "data": {"credit_types": credit_types, "request_statuses": request_statuses}
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@requestRouter.post("/")
async def create_request(
    request: RequestCreate,
    db: Session = Depends(get_session),
    mail_service: MailService = Depends(get_mail_service),
):

    try:
        new_request, is_created = await RequestService(db, mail_service).create_request(
            request
        )
        if is_created:
            return {"message": "Solicitud creada exitosamente", "data": new_request}
        else:
            return {
                "message": "Solicitud actualizada exitosamente",
                "data": new_request,
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear solicitud: {e}",
        )


@requestRouter.get("/")
def get_requests(db: Session = Depends(get_session)):
    requests = RequestService(db).get_all_requests()
    return {"data": requests}


@requestRouter.get("/paginated-list")
async def get_paginated_list(
    client_id: Optional[UUID] = Query(
        None,
        description="ID del cliente para filtrar las solicitudes.",
    ),
    db: Session = Depends(get_session),
    page: int = Query(
        1,
        ge=1,
        description="Número de página para la paginación.",
    ),
    per_page: int = Query(
        10,
        ge=1,
        le=100,
        description="Número de elementos por página para la paginación.",
    ),
    status_id: Optional[UUID] = Query(
        None, description="Filtrar por ID de estado de la solicitud."
    ),
    credit_type_id: Optional[UUID] = Query(
        None, description="Filtrar por ID de tipo de crédito."
    ),
    order_by: Optional[str] = Query(
        None, description="Campo por el cual ordenar los resultados."
    ),
    sort_order: Optional[str] = Query(
        "asc", description="Orden de los resultados (asc/desc)."
    ),
):
    service = RequestService(db)
    try:
        requests_list, total_items = await service.get_paginated_list(
            client_id=client_id,
            page=page,
            per_page=per_page,
            status_id=status_id,
            credit_type_id=credit_type_id,
            order_by=order_by,
            sort_order=sort_order,
        )

        total_pages = (total_items + per_page - 1) // per_page
        current_page = page
        has_previous_page = current_page > 1
        has_next_page = current_page < total_pages

        pagination_meta = PaginationMeta(
            page=current_page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_previous_page=has_previous_page,
            has_next_page=has_next_page,
        )

        return PaginatedRequestsResponse(data=requests_list, pagination=pagination_meta)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener solicitudes: {e}",
        )


@requestRouter.get("/{id}")
def get_request_by_id(id: UUID, db: Session = Depends(get_session)):
    request = RequestService(db).get_request_by_id(id)
    return {"data": request}


@requestRouter.patch("/{id}")
def update_request(
    id: UUID, request_update: RequestUpdate, db: Session = Depends(get_session)
):
    updated_request = RequestService(db).update_request(id, request_update)
    return {"message": "Solicitud actualizada exitosamente", "data": updated_request}


@requestRouter.patch("/{id}/approve")
async def approve_request(
    body: RequestApprove,
    id: UUID,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(jwt_guard),
    mail_service: MailService = Depends(get_mail_service),
):
    updated_request = await RequestService(db, mail_service).approve_request(
        id, user_id, body.approved_amount
    )
    return {"message": "Solicitud aprobada exitosamente", "data": updated_request}


@requestRouter.patch("/{id}/reject")
async def reject_request(
    body: RequestReject,
    id: UUID,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(jwt_guard),
    mail_service: MailService = Depends(get_mail_service),
):
    updated_request = await RequestService(db, mail_service).reject_request(
        id, user_id, body.rejection_reason
    )
    return {"message": "Solicitud rechazada exitosamente", "data": updated_request}


@requestRouter.patch("/{id}/change-status")
def change_status(
    body: RequestChangeStatus,
    id: UUID,
    db: Session = Depends(get_session),
):
    updated_request = RequestService(db).change_status(id, body.status_id)
    return {
        "message": "Estado de la solicitud cambiado exitosamente",
        "data": updated_request,
    }


@requestRouter.delete("/{id}")
def delete_request(id: UUID, db: Session = Depends(get_session)):
    RequestService(db).delete_request(id)
    return {"message": "Solicitud eliminada exitosamente"}


@requestRouter.get("/client/{client_id}")
def get_request_by_client_id(client_id: UUID, db: Session = Depends(get_session)):
    request = RequestService(db).get_request_by_client_id(client_id)
    return {"data": request}
