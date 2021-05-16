from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from passlib.hash import bcrypt

from gram.depends import current_user
from gram.models import Post, User
from gram.schemas import (
    PydanticPost,
    PydanticUser,
    PydanticUserCreate,
    PydanticUserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=PydanticUser,
    dependencies=[Depends(RateLimiter(times=5, hours=1))],
)
async def create_user(user: PydanticUserCreate):
    user_record = await User.create(
        username=user.username,
        mail=user.mail,
        password=bcrypt.hash(user.password),
        bio=user.bio,
    )
    return await PydanticUser.from_tortoise_orm(user_record)


@router.patch(
    "/me",
    response_model=PydanticUser,
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def update_logged_in_user(
    updated_user: Optional[PydanticUserUpdate],
    user: User = Depends(current_user),
):
    if updated_user.password:
        print(updated_user.password, bcrypt.hash(updated_user.password))
        updated_user.password = bcrypt.hash(updated_user.password)

    await user.update_from_dict(updated_user.dict(exclude_unset=True)).save()

    return await PydanticUser.from_tortoise_orm(user)


# TODO: Account deleting and disabling


@router.get("/me", response_model=PydanticUser)
async def get_logged_in_user(user: User = Depends(current_user)):
    return await PydanticUser.from_tortoise_orm(user)


@router.get("/me/posts", response_model=list[PydanticPost])
async def get_logged_in_user_posts(user: User = Depends(current_user)):
    return await PydanticPost.from_queryset(Post.filter(author=user))


@router.get("/{user_id}", response_model=PydanticUser)
async def get_user(user_id: int):
    return await PydanticUser.from_queryset_single(User.get(id=user_id))


@router.get("/{user_id}/posts", response_model=list[PydanticPost])
async def get_user_posts(user_id: int):
    user_record = await User.get(id=user_id)
    return await PydanticPost.from_queryset(Post.filter(author=user_record))
