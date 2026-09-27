from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_user_repository, require_role
from app.core.exceptions import NotFoundError
from app.models.user import UserPublic
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublic], dependencies=[Depends(require_role("admin"))])
async def list_users(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Admin-only: list all registered users."""
    users = await user_repo.list(skip=skip, limit=limit)
    return [UserPublic(**u.model_dump()) for u in users]


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(require_role("admin"))])
async def get_user(user_id: str, user_repo: Annotated[UserRepository, Depends(get_user_repository)]):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return UserPublic(**user.model_dump())


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_role("admin"))])
async def delete_user(user_id: str, user_repo: Annotated[UserRepository, Depends(get_user_repository)]):
    deleted = await user_repo.delete(user_id)
    if not deleted:
        raise NotFoundError("User", user_id)
