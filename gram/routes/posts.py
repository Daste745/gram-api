from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from tortoise.contrib.fastapi import HTTPNotFoundError

from gram.depends import current_user
from gram.models import Comment, Post, User
from gram.schemas import (
    HTTPForbiddenError,
    PydanticComment,
    PydanticCommentCreate,
    PydanticCommentUpdate,
    PydanticPost,
    PydanticPostCreate,
    PydanticPostUpdate,
    Status,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=PydanticPost,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
async def create_post(
    post: PydanticPostCreate,
    user: User = Depends(current_user),
):
    post_record = await Post.create(
        **post.dict(exclude_unset=True),
        author=user,
    )
    return await PydanticPost.from_tortoise_orm(post_record)


@router.patch(
    "/{post_id}",
    response_model=PydanticPost,
    responses={
        404: {"model": HTTPNotFoundError},
        403: {"model": HTTPForbiddenError},
    },
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def update_post(
    post_id: UUID,
    updated_post: PydanticPostUpdate,
    user: User = Depends(current_user),
):
    post_record = await Post.get(id=post_id)
    if not user == post_record.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other user's post",
        )

    await post_record.update_from_dict(updated_post.dict(exclude_unset=True))

    return await PydanticPost.from_tortoise_orm(post_record)


@router.delete(
    "/{post_id}",
    response_model=Status,
    responses={
        404: {"model": HTTPNotFoundError},
        403: {"model": HTTPForbiddenError},
    },
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
async def delete_post(post_id: UUID, user: User = Depends(current_user)):
    post_record = await Post.get(id=post_id).prefetch_related("author")
    if not user == post_record.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other user's post",
        )

    await post_record.delete()

    return Status(detail=f"Deleted post {post_id}")


@router.get(
    "/{post_id}",
    response_model=PydanticPost,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_post(post_id: UUID):
    return await PydanticPost.from_queryset_single(Post.get(id=post_id))
