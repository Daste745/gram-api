from fastapi import HTTPException, status
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from gram.models import Comment, Post, User

InvalidCredentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

ExpiredToken = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access token has expired",
    headers={"WWW-Authenticate": "Bearer"},
)


class Token(BaseModel):
    access_token: str
    token_type: str


class Status(BaseModel):
    detail: str


class HTTPForbiddenError(BaseModel):
    detail: str


# region User


class UserUpdateCreateMeta:
    exclude = ()


PydanticUser = pydantic_model_creator(
    User,
    name="User",
)


PydanticUserCreate = pydantic_model_creator(
    User,
    name="UserCreate",
    exclude_readonly=True,
    meta_override=UserUpdateCreateMeta,
)


PydanticUserUpdate = pydantic_model_creator(
    User,
    name="UserUpdate",
    exclude_readonly=True,
    optional=("username", "mail", "password", "bio"),
    meta_override=UserUpdateCreateMeta,
)


# endregion User


# region Post


PydanticPost = pydantic_model_creator(
    Post,
    name="Post",
)


PydanticPostCreate = pydantic_model_creator(
    Post,
    name="PostCreate",
    exclude_readonly=True,
    exclude=("author_id",),
)


PydanticPostUpdate = pydantic_model_creator(
    Post,
    name="PostUpdate",
    exclude_readonly=True,
    exclude=("author_id",),
    optional=("title", "content", "image_url"),
)


# endregion Post


# region Comment


PydanticComment = pydantic_model_creator(
    Comment,
    name="Comment",
)


PydanticCommentCreate = pydantic_model_creator(
    Comment,
    name="CommentCreate",
    exclude_readonly=True,
    exclude=("author_id", "post_id"),
)


PydanticCommentUpdate = pydantic_model_creator(
    Comment,
    name="CommentUpdate",
    exclude_readonly=True,
    exclude=("author_id", "post_id"),
    optional=("content",),
)


# endregion Comment
