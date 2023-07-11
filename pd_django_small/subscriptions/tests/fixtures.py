import factory
from pytest_factoryboy import register

from pd_django_small.subscriptions.models import Subscription


@register
class SubscriptionFactory(factory.django.DjangoModelFactory):
    quantity = factory.Sequence(lambda n: n)

    class Meta:
        model = Subscription
