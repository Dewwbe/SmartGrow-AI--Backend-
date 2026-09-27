"""
Auth business logic: register, login, refresh, logout.

Kept separate from the API layer so it's independently testable and so the
future AI agent (or an admin CLI, etc.) can reuse the same login/registration
logic without going through HTTP.
"""
import uuid

from app.core.exceptions import DuplicateError, InvalidCredentialsError, InvalidTokenError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import UserCreate, UserInDB, UserLogin
from app.repositories.token_repository import TokenDenylistRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository, token_denylist: TokenDenylistRepository):
        self.user_repo = user_repo
        self.token_denylist = token_denylist

    async def register(self, payload: UserCreate) -> UserInDB:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise DuplicateError("User", "email", payload.email)

        document = {
            "email": payload.email.lower(),
            "full_name": payload.full_name,
            "role": payload.role,
            "hashed_password": hash_password(payload.password),
            "is_active": True,
        }
        return await self.user_repo.create(document)

    async def authenticate(self, payload: UserLogin) -> UserInDB:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError()
        return user

    def issue_tokens(self, user: UserInDB) -> dict[str, str]:
        access_token = create_access_token(subject=user.id, extra_claims={"role": user.role})
        refresh_jti = str(uuid.uuid4())
        refresh_token = create_refresh_token(subject=user.id, jti=refresh_jti)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidTokenError()

        jti = payload.get("jti")
        if not jti or await self.token_denylist.is_revoked(jti):
            raise InvalidTokenError("Refresh token has been revoked")

        user = await self.user_repo.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise InvalidTokenError("User no longer active")

        access_token = create_access_token(subject=user.id, extra_claims={"role": user.role})
        return {"access_token": access_token, "token_type": "bearer"}

    async def logout(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        if payload and payload.get("type") == "refresh" and payload.get("jti"):
            await self.token_denylist.revoke(payload["jti"])
