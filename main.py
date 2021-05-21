from aioredis import create_redis_pool
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from tortoise.contrib.fastapi import register_tortoise
from tortoise.validators import ValidationError

from gram.models import User
from gram.routes import comments, posts, users
from gram.schemas import InvalidCredentials, Token
from gram.utils import db_connection_string, redis_connection_string

api = FastAPI(
    title="Gram",
    description="An Instagram clone",
    dependencies=[Depends(RateLimiter(times=1, seconds=1))],
)
api.include_router(users.router)
api.include_router(posts.router)
api.include_router(comments.router)


@api.on_event("startup")
async def startup():
    register_tortoise(
        api,
        modules={"models": ["gram.models"]},
        db_url=db_connection_string(),
        generate_schemas=True,
        add_exception_handlers=True,
    )
    redis = await create_redis_pool(redis_connection_string())
    FastAPILimiter.init(redis)


@api.post(
    "/token",
    response_model=Token,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    tags=["auth"],
)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(username=form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise InvalidCredentials

    token: str = user.access_token()
    return Token(access_token=token, token_type="bearer")


@api.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )
