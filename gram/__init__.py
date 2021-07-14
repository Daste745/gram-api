import os

from aioredis import create_redis_pool
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from tortoise.contrib.fastapi import register_tortoise
from tortoise.validators import ValidationError

from gram.routes import auth, comments, posts, users
from gram.utils import db_connection_string, redis_connection_string

api = FastAPI(
    title="Gram",
    description="An Instagram clone",
    dependencies=[Depends(RateLimiter(times=1, seconds=1))],
)
api.include_router(auth.router)
api.include_router(users.router)
api.include_router(posts.router)
api.include_router(comments.router)

if os.path.isfile(".env"):
    load_dotenv()

TORTOISE_CONFIG = {
    "connections": {
        "default": db_connection_string(),
    },
    "apps": {
        "models": {
            "models": ["gram.models", "aerich.models"],
        },
    },
}


@api.on_event("startup")
async def startup():
    register_tortoise(
        api,
        config=TORTOISE_CONFIG,
        add_exception_handlers=True,
    )
    redis = await create_redis_pool(redis_connection_string())
    FastAPILimiter.init(redis)


@api.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )
