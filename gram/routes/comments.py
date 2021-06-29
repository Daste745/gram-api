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
    Status,
)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/{post_id}",
    response_model=PydanticComment,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
async def create_post_comment(
    post_id: UUID,
    comment: PydanticCommentCreate,
    user: User = Depends(current_user),
):
    post_record = await Post.get(id=post_id)
    comment_record = await Comment.create(
        author=user,
        post=post_record,
        **comment.dict(exclude_unset=True),
    )

    return await PydanticComment.from_tortoise_orm(comment_record)


@router.patch(
    "/{post_id}/{comment_id}",
    response_model=PydanticComment,
    responses={
        404: {"model": HTTPNotFoundError},
        403: {"model": HTTPForbiddenError},
    },
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def update_post_comment(
    post_id: UUID,
    comment_id: UUID,
    updated_comment: PydanticCommentUpdate,
    user: User = Depends(current_user),
):
    post_record = await Post.get(id=post_id)
    comment_record = await Comment.get(id=comment_id)

    if not post_record == comment_record.post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The comment {comment_id} does not belong to post {post_id}",
        )

    if not user == comment_record.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other user's comments",
        )

    await comment_record.update_from_dict(updated_comment.dict(exclude_unset=True))
    return await PydanticComment.from_tortoise_orm(comment_record)


@router.delete(
    "/{post_id}/{comment_id}",
    response_model=Status,
    responses={
        404: {"model": HTTPNotFoundError},
        403: {"model": HTTPForbiddenError},
    },
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
async def delete_post_comment(
    post_id: UUID,
    comment_id: UUID,
    user: User = Depends(current_user),
):
    post_record = await Post.get(id=post_id)
    comment_record = await Comment.get(id=comment_id)

    if not user == comment_record.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other user's comments",
        )

    await post_record.delete()

    return Status(detail=f"Deleted comment {comment_id} from post {post_id}")


@router.get(
    "/{post_id}",
    response_model=list[PydanticComment],
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_post_comments(post_id: UUID):
    post_record = await Post.get(id=post_id)
    return await PydanticComment.from_queryset(Comment.filter(post=post_record))


@router.get(
    "/{post_id}/{comment_id}",
    response_model=PydanticComment,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_post_comment(post_id: UUID, comment_id: UUID):
    post_record = await Post.get(id=post_id)
    return await PydanticComment.from_queryset_single(
        Comment.filter(id=comment_id, post=post_record)
    )
