import pytest

from pd_django_small.organizations.models import Organization
from pd_django_small.subscriptions.models import SubscriptionState

from django.contrib.postgres.aggregates import ArrayAgg

from pd_django_small.workspaces.models import Workspace

from django.db.models import (
    F,
    Func,
    IntegerField,
    OuterRef,
    Subquery,
)

@pytest.mark.django_db
def test_organizations_annotate(organization_factory, workspace_factory, user_factory):
    """
    Select all organizations, annotate all not removed workspaces uuid (as array::UUID)
    and annotate total number of workspaces.
    """

    # Arrange
    owner1, owner2 = user_factory.create_batch(2)

    organization1 = organization_factory.create(owner=owner1.uuid)
    workspace1 = workspace_factory.create(
        owner=owner1.uuid, organization=organization1.uuid
    )

    organization2 = organization_factory.create(owner=owner2.uuid)
    workspace2 = workspace_factory.create(
        owner=owner2.uuid, organization=organization2.uuid
    )
    workspace3 = workspace_factory.create(
        owner=owner2.uuid, organization=organization2.uuid
    )
    workspace_factory.create(
        owner=owner2.uuid, organization=organization2.uuid, is_removed=True
    )

    # Act
    qs = Organization.objects.annotate(
        workspaces=Subquery(
            Workspace.objects.filter(
                organization=OuterRef("uuid"), is_removed=False
            ).values("organization")
            .annotate(uuids=ArrayAgg("uuid"))
            .values("uuids")
        ),
        workspaces_count=Subquery(
            Workspace.objects.filter(
                organization=OuterRef("uuid")
            ).annotate(
                count=Func(F("uuid"), function="Count")
            ).values("count")
        )
    )

    # Assert
    for organization, (workspaces_count, workspaces) in zip(
        qs, ((1, [workspace1.uuid]), (3, [workspace2.uuid, workspace3.uuid]))
    ):
        assert organization.workspaces_count == workspaces_count
        assert organization.workspaces == workspaces


@pytest.mark.django_db
def test_organizations_subscription(
    organization_factory, workspace_factory, user_factory, subscription_factory
):
    """
    Select all organizations, where number of workspaces is more than 2
    and subscription state is active and subscription price in range (50, 100).
    """

    # Arrange
    owner1, owner2, owner3, owner4, owner5 = user_factory.create_batch(5)

    organization1 = organization_factory.create(owner=owner1.uuid)
    workspace_factory.create_batch(
        3, owner=owner1.uuid, organization=organization1.uuid
    )
    subscription_factory.create(
        organization=organization1, state=SubscriptionState.ACTIVE.value, price=99
    )

    organization2 = organization_factory.create(owner=owner2.uuid)
    workspace_factory.create_batch(
        5, owner=owner2.uuid, organization=organization2.uuid
    )
    subscription_factory.create(
        organization=organization2, state=SubscriptionState.ACTIVE.value, price=80
    )

    organization3 = organization_factory.create(owner=owner3.uuid)
    workspace_factory.create(owner=owner3.uuid, organization=organization3.uuid)
    subscription_factory.create(
        organization=organization3, state=SubscriptionState.ACTIVE.value, price=100
    )

    organization4 = organization_factory.create(owner=owner4.uuid)
    workspace_factory.create_batch(
        5, owner=owner4.uuid, organization=organization4.uuid
    )
    subscription_factory.create(
        organization=organization4, state=SubscriptionState.EXPIRED.value, price=80
    )

    organization5 = organization_factory.create(owner=owner5.uuid)
    workspace_factory.create_batch(
        5, owner=owner5.uuid, organization=organization5.uuid
    )
    subscription_factory.create(
        organization=organization5, state=SubscriptionState.ACTIVE.value, price=20
    )

    """
    Select all organizations, where number of workspaces is more than 2
    and subscription state is active and subscription price in range (50, 100).
    """
    # Act
    qs = Organization.objects.filter(
        subscription__state=SubscriptionState.ACTIVE.value,
        subscription__price__range=(50, 100),
    ).annotate(
        workspaces_count=Subquery(
            Workspace.objects.filter(
                organization=OuterRef("uuid")
            ).annotate(
                ws_count=Func(F("uuid"), function="Count")
            ).values("ws_count"),
            output_field=IntegerField(),
        )
    ).filter(
        workspaces_count__gt=2
    )

    # Assert
    for expected_organization, organization in zip(qs, [organization1]):
        assert organization.uuid == organization.uuid
