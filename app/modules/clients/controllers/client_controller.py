from uuid import UUID
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.modules.clients.dtos.client_dto import ClientProfileCreate, ClientProfileUpdate
from app.modules.clients.services.client_service import (
    ClientProfileNotFoundError,
    ClientProfileService,
)
from app.shared.guards.jwtGuard import jwt_guard
from fastapi import HTTPException, status

clientRouter = APIRouter(
    prefix="/clients",
    tags=["Clientes"],
    dependencies=[Depends(jwt_guard)],
)


@clientRouter.post("/")
def create_client(request: ClientProfileCreate, db: Session = Depends(get_session)):
    try:
        new_client, is_created = ClientProfileService(db).create_client_profile(request)
        if is_created:
            return {"message": "Cliente creado exitosamente", "data": new_client}
        else:
            return {"message": "Cliente actualizado exitosamente", "data": new_client}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@clientRouter.get("/{user_id}")
def get_client_profile(user_id: UUID, db: Session = Depends(get_session)):
    try:
        client_profile = ClientProfileService(db).get_client_profile_by_user_id(user_id)
        return {"data": client_profile}
    except ClientProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@clientRouter.patch("/{user_id}")
def update_client_profile(
    user_id: UUID, request: ClientProfileUpdate, db: Session = Depends(get_session)
):
    try:
        updated_client = ClientProfileService(db).update_client_profile(
            user_id, request
        )
        return {
            "message": "Perfil de cliente actualizado exitosamente",
            "data": updated_client,
        }
    except ClientProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@clientRouter.delete("/{user_id}")
def delete_client_profile(user_id: UUID, db: Session = Depends(get_session)):
    try:
        ClientProfileService(db).delete_client_profile(user_id)
        return {"message": "Perfil de cliente eliminado exitosamente"}
    except ClientProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
