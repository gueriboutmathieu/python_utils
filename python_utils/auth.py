from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode  # pyright: ignore
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from typing import Annotated, Any


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthException(Exception):
    def __init__(self, message: str = "Auth exception") -> None:
        self.message = message


class Auth:
    def __init__(
        self,
        secret_key: str,
        public_key: str,
        token_data_keys: list[str] = ["username"],
        access_token_expire_seconds: int = 86400,  # 1 day
        refresh_token_expire_days: int = 30,  # 30 days
    ) -> None:
        self.secret_key = secret_key
        self.public_key = public_key
        self.algorithm = "HS256"

        if len(token_data_keys) == 0 or "username" not in token_data_keys:
            raise AuthException("Invalid token data keys")

        self.token_data_keys = token_data_keys
        self.access_token_expire_seconds = access_token_expire_seconds
        self.refresh_token_expire_days = refresh_token_expire_days

    def validate_public_key(self, public_key: str) -> None:
        if public_key != self.public_key:
            raise AuthException("Invalid public key")

    def create_access_token(self, token_data: dict[str, Any]) -> str:
        if all(key not in token_data for key in self.token_data_keys):
            raise AuthException("Missing required data in token")

        expire = datetime.now(timezone.utc) + timedelta(seconds=self.access_token_expire_seconds)
        token_data.update({"expire": expire.isoformat()})
        access_token = encode(token_data, self.secret_key, algorithm=self.algorithm)
        return access_token

    def create_refresh_token(self, token_data: dict[str, Any]) -> str:
        if all(key not in token_data for key in self.token_data_keys):
            raise AuthException("Missing required data in token")

        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        token_data.update({"expire": expire.isoformat()})
        refresh_token = encode(token_data, self.secret_key, algorithm=self.algorithm)
        return refresh_token

    def validate_token(self, token: str) -> None:
        try:
            decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise AuthException("Token expired")
        except PyJWTError:
            raise AuthException("Invalid token")

    def refresh_access_token(self, refresh_token: str) -> str:
        try:
            self.validate_token(refresh_token)
        except AuthException:
            raise
        payload = decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
        token_data: dict[str, Any] = {}
        for key in self.token_data_keys:
            if key not in payload:
                raise AuthException(f"Missing {key} in token")
            token_data[key] = payload[key]

        access_token = self.create_access_token(token_data)
        return access_token

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> str:
        try:
            self.validate_token(token)
        except AuthException:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        payload = decode(token, self.secret_key, algorithms=[self.algorithm])
        username = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return username
