from tortoise import Tortoise

from .models import Comment, Post, User

Tortoise.init_models([__name__], "models")
