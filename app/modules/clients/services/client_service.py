from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.clients.dtos.client_dto import (
    ClientProfileResponse,
    ClientProfileUpdate,
)
from app.modules.clients.models.client_model import ClientInterface
from app.shared.entities.client_profile_entity import ClientProfile


class ClientProfileNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de cliente no encontrado.",
        )


class ClientProfileAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un perfil de cliente.",
        )


class ClientProfileService:
    def __init__(self, db: Session):
        self.db = db

    def _client_exists(self, user_id: UUID) -> bool:
        return self.db.get(ClientProfile, user_id)

    def create_client_profile(
        self, profile_data: ClientInterface
    ) -> ClientProfileResponse:

        if self._client_exists(profile_data.user_id) is not None:
            user_updated = self.update_client_profile(
                profile_data.user_id, profile_data
            )
            return user_updated, False

        db_profile = ClientProfile(**profile_data.dict())
        db_profile.created_at = datetime.now()
        db_profile.updated_at = datetime.now()

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return ClientProfileResponse.model_validate(db_profile), True

    def get_client_profile_by_user_id(self, user_id: UUID) -> ClientProfileResponse:
        db_profile = self.db.get(ClientProfile, user_id)
        if not db_profile:
            raise ClientProfileNotFoundError()
        return ClientProfileResponse.model_validate(db_profile)

    def update_client_profile(
        self, user_id: UUID, profile_data: ClientProfileUpdate
    ) -> ClientProfileResponse:
        db_profile = self.db.get(ClientProfile, user_id)
        if not db_profile:
            raise ClientProfileNotFoundError()

        update_data = profile_data.model_dump(exclude_unset=True)
        db_profile.sqlmodel_update(update_data)
        db_profile.updated_at = datetime.now()

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return ClientProfileResponse.model_validate(db_profile)

    def delete_client_profile(self, user_id: UUID) -> bool:
        db_profile = self.db.get(ClientProfile, user_id)
        if not db_profile:
            raise ClientProfileNotFoundError()

        self.db.delete(db_profile)
        self.db.commit()
        return True
