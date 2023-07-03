import uuid
from django.db import models
from django.core.validators import MinValueValidator
from enum import Enum

from pd_django_small.organizations.models import Organization


class SubscriptionState(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Subscription(models.Model):
    uuid = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    state = models.CharField(
        max_length=16,
        choices=SubscriptionState.choices(),
    )
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.CharField(max_length=255, null=True)
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
