import factory
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from pd_django_small.workspaces.models import Membership, Workspace

faker = FakerFactory.create()


@register
class WorkspaceFactory(factory.django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: faker.company())

    class Meta:
        model = Workspace


@register
class MembershipFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Membership
