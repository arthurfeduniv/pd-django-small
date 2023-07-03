import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum


class AccountType(Enum):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class User(AbstractUser):
    uuid = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=82, blank=False)
    last_name = models.CharField(max_length=82, blank=False)
    is_active = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    account_type = models.CharField(
        max_length=16,
        choices=AccountType.choices()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
