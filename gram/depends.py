from os import getenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from gram.models import User
from gram.schemas import ExpiredToken, InvalidCredentials

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, getenv("JWT_SECRET"), algorithms=["HS256"])
        # TODO: Expire token if user changed their password
        #       This needs to be done statelessly - no saving tokens in the db
        user = await User.get_or_none(id=payload.get("sub"))
    except ExpiredSignatureError:
        raise ExpiredToken
    except JWTError:
        raise InvalidCredentials

    if not user:
        raise InvalidCredentials

    return user
