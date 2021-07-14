from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter

from gram.models import User
from gram.schemas import InvalidCredentials, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
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
