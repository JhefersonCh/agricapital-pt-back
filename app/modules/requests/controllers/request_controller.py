from typing import Optional
from uuid import UUID
from fastapi import Depends, APIRouter, Query
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.modules.requests.dtos.crud_request_dto import RequestCreate, RequestUpdate
from app.modules.requests.services.request_service import RequestService
from app.shared.dtos.pagination_dto import PaginatedRequestsResponse, PaginationMeta
from app.shared.guards.jwtGuard import jwt_guard
from fastapi import HTTPException, status

requestRouter = APIRouter(
    prefix="/requests",
    tags=["Solicitudes de crédito"],
    dependencies=[Depends(jwt_guard)],
)


@requestRouter.post("/")
def create_request(request: RequestCreate, db: Session = Depends(get_session)):
    try:
        new_request = RequestService(db).create_request(request)
        return {"message": "Solicitud creada exitosamente", "data": new_request}
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
    client_id: UUID = Depends(jwt_guard),
    db: Session = Depends(get_session),
    offset: int = Query(
        0, ge=0, description="Número de elementos a omitir (para paginación)."
    ),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="Número máximo de elementos a retornar (para paginación).",
    ),
    status_id: Optional[UUID] = Query(
        None, description="Filtrar por ID de estado de la solicitud."
    ),
    credit_type_id: Optional[UUID] = Query(
        None, description="Filtrar por ID de tipo de crédito."
    ),
):
    service = RequestService(db)
    try:
        requests_list, total_items = await service.get_paginated_list(
            client_id=client_id,
            offset=offset,
            limit=limit,
            status_id=status_id,
            credit_type_id=credit_type_id,
        )

        total_pages = (total_items + limit - 1) // limit
        current_page = (offset // limit) + 1
        has_previous_page = current_page > 1
        has_next_page = current_page < total_pages

        pagination_meta = PaginationMeta(
            page=current_page,
            per_page=limit,
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


@requestRouter.delete("/{id}")
def delete_request(id: UUID, db: Session = Depends(get_session)):
    RequestService(db).delete_request(id)
    return {"message": "Solicitud eliminada exitosamente"}
