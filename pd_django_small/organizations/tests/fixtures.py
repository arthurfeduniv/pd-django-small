import factory
from faker import Factory as FakerFactory
from pytest_factoryboy import register
from factory.faker import Faker

from pd_django_small.organizations.models import Organization

faker = FakerFactory.create()


@register
class OrganizationFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda _: faker.company())

    class Meta:
        model = Organization

