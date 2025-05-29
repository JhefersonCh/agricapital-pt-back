from dotenv import load_dotenv
from fastapi import HTTPException
from jose import jwt, JWTError
import os

load_dotenv()


class JwtService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = os.getenv("JWT_ALGORITHM")
        self.audience = os.getenv("JWT_AUDIENCE")

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
            )

            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        except Exception:
            raise HTTPException(
                status_code=500, detail="Error interno al verificar token"
            )
