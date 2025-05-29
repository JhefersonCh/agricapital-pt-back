from uuid import UUID
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from fastapi import Depends, HTTPException, status
from app.shared.services.jwtService import JwtService

security = HTTPBearer()


def jwt_guard(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    token = credentials.credentials
    try:
        payload = JwtService().verify_token(token)

        user_id_str: str = payload.get("sub")

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: ID de usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UUID(user_id_str)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario en el token no es un UUID válido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado de autenticación: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
