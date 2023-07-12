import factory
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from pd_django_small.users.models import User

faker = FakerFactory.create()


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda _: faker.email())

    class Meta:
        model = User
