import uuid
from django.db import models


class Organization(models.Model):
    uuid = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=255, blank=False)
    owner = models.UUIDField(
        unique=True,
        verbose_name="user uuid",
    )
