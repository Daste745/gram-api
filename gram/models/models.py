import re
from datetime import datetime, timedelta
from os import getenv
from typing import Union

from jose import jwt
from passlib.hash import bcrypt
from tortoise.fields import (
    CharField,
    DatetimeField,
    ForeignKeyField,
    ForeignKeyRelation,
    IntField,
    ReverseRelation,
    TextField,
)
from tortoise.models import Model
from tortoise.validators import MinLengthValidator, RegexValidator


class User(Model):
    id = IntField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    modified_at = DatetimeField(auto_now=True)
    username = CharField(
        max_length=32,
        unique=True,
        validators=[
            MinLengthValidator(2),
            RegexValidator(r"^[a-z0-9._-]+$", re.I),
        ],
    )
    mail = CharField(
        max_length=64,
        null=True,
        validators=[
            RegexValidator(
                r"^[\w.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                re.I,
            )
        ],
    )
    password = CharField(max_length=64, validators=[MinLengthValidator(8)])
    bio = TextField(null=True)

    posts = ReverseRelation["Post"]
    comments = ReverseRelation["Comment"]

    class Meta:
        table = "users"

    class PydanticMeta:
        exclude = ("password", "access_token", "posts", "comments")

    def __repr__(self):
        return (
            f"User({self.id=}, {self.created_at=}, {self.modified_at=}, "
            f"{self.username=}, {self.mail=}, {self.password=},{self.bio=})"
        )

    def __str__(self):
        return self.__repr__()

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password)

    def access_token(self) -> str:
        data: dict[str, Union[datetime, str]] = {
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=60),
            "sub": str(self.id),
        }
        token: str = jwt.encode(
            data,
            getenv("JWT_SECRET"),
            algorithm="HS256",
        )
        return token


class Post(Model):
    id = IntField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    modified_at = DatetimeField(auto_now=True)
    title = CharField(max_length=32)
    content = TextField(null=True)
    image_url = TextField()

    author: ForeignKeyRelation[User] = ForeignKeyField("models.User", "posts")
    comments = ReverseRelation["Comment"]

    class Meta:
        table = "posts"
        ordering = ["created_at"]

    class PydanticMeta:
        exclude = ("author", "comments")

    def __repr__(self):
        return (
            f"Post({self.id=}, {self.created_at=}, {self.modified_at=}, "
            f"{self.title=}, {self.content=}, {self.image_url}, {self.author=})"
        )

    def __str__(self):
        return self.__repr__()


class Comment(Model):
    id = IntField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    modified_at = DatetimeField(auto_now=True)
    content = TextField()

    author: ForeignKeyRelation[User] = ForeignKeyField("models.User", "comments")
    post: ForeignKeyRelation[Post] = ForeignKeyField("models.Post", "comments")

    class Meta:
        table = "comments"
        ordering = ["created_at"]

    class PydanticMeta:
        exclude = ("author", "post")

    def __repr__(self):
        return (
            f"Comment({self.id=}, {self.created_at=}, {self.modified_at=}, "
            f"{self.content=}, {self.author=}, {self.post=})"
        )

    def __str__(self):
        return self.__repr__()
