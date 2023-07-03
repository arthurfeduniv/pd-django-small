import uuid
from django.db import models


class Workspace(models.Model):
    uuid = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=82)
    owner = models.UUIDField(
        verbose_name="user uuid",
    )
    organization = models.UUIDField(
        verbose_name="organization uuid",
    )
    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Membership(models.Model):
    uuid = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
    )
    user = models.UUIDField(
        verbose_name="user uuid",
    )
    is_active = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "membership"
        verbose_name_plural = "memberships"
        db_table = "workspaces_membership"
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_active=True),
                name="unique_user_active_membership"
            )
        ]
