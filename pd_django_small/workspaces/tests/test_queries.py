import pytest

from pd_django_small.workspaces.models import Workspace
from pd_django_small.organizations.models import Organization
from django.db.models import OuterRef, Window
from django.db.models.functions import Lag, Lead


@pytest.mark.django_db
def test_workspaces_annotate(organization_factory, workspace_factory, user_factory):
    """Select all workspaces where owner is organization owner."""

    # Arrange
    owner1, owner2 = user_factory.create_batch(2)
    user1, user2 = user_factory.create_batch(2)

    organization1 = organization_factory.create(owner=owner1.uuid)
    workspace_factory.create(owner=owner1.uuid, organization=organization1.uuid)

    organization2 = organization_factory.create(owner=owner2.uuid)
    workspace_factory.create(owner=owner2.uuid, organization=organization2.uuid)

    workspace_factory.create(owner=user1.uuid, organization=organization2.uuid)
    workspace_factory.create(owner=user2.uuid, organization=organization2.uuid)

    # Act
    qs = None

    # Assert
    for workspace, owner in zip(qs, [owner1, owner2]):
        assert workspace.owner == owner.uuid


@pytest.mark.django_db
def test_workspaces_next_prev_uuid(
    organization_factory, workspace_factory, user_factory
):
    """
    Select all workspaces, annotate next_workspace_uuid and prev_workspace_uuid for each workspace.
    (e.g.

    uuid: b20c73ee
    prev_workspace_uuid: None
    next_workspace_uuid: 2a858c87

    uuid: 2a858c87
    prev_workspace_uuid: b20c73ee
    next_workspace_uuid: eb2cc75e

    uuid: eb2cc75e
    prev_workspace_uuid: 2a858c87
    next_workspace_uuid: None

    """

    # Arrange
    owner = user_factory.create()
    organization = organization_factory.create(owner=owner.uuid)
    workspace1, workspace2, workspace3 = workspace_factory.create_batch(
        3, owner=owner.uuid, organization=organization.uuid
    )

    # Act
    qs = None

    # Assert
    assert qs[0].uuid == workspace1.uuid
    assert qs[0].prev_workspace_uuid is None
    assert qs[0].next_workspace_uuid == workspace2.uuid

    assert qs[1].uuid == workspace2.uuid
    assert qs[1].prev_workspace_uuid == workspace1.uuid
    assert qs[1].next_workspace_uuid == workspace3.uuid

    assert qs[2].uuid == workspace3.uuid
    assert qs[2].prev_workspace_uuid == workspace2.uuid
    assert qs[2].next_workspace_uuid is None
