import pytest
from django.db.models import Case, When, Value, IntegerField, Sum, F, DecimalField, Q
from django.db.models.functions import Least

from pd_django_small.subscriptions.models import SubscriptionState, Subscription
from pd_django_small.users.models import User


@pytest.mark.django_db
def test_subscription_orders(organization_factory, user_factory, subscription_factory):
    """
    Select all subscriptions, in next order (CANCELLED, EXPIRED, ACTIVE) and price desc.
    """

    # Arrange
    owner1, owner2, owner3, owner4, owner5 = user_factory.create_batch(5)

    subscription1 = subscription_factory.create(
        organization=organization_factory.create(owner=owner1.uuid),
        state=SubscriptionState.EXPIRED.value,
        price=100,
    )
    subscription2 = subscription_factory.create(
        organization=organization_factory.create(owner=owner2.uuid),
        state=SubscriptionState.ACTIVE.value,
        price=20,
    )
    subscription3 = subscription_factory.create(
        organization=organization_factory.create(owner=owner3.uuid),
        state=SubscriptionState.CANCELLED.value,
        price=200,
    )
    subscription4 = subscription_factory.create(
        organization=organization_factory.create(owner=owner4.uuid),
        state=SubscriptionState.EXPIRED.value,
        price=310,
    )
    subscription5 = subscription_factory.create(
        organization=organization_factory.create(owner=owner5.uuid),
        state=SubscriptionState.CANCELLED.value,
        price=12,
    )

    # Act
    qs = Subscription.objects.order_by(
        Case(
            When(state=SubscriptionState.CANCELLED.value, then=1),
            When(state=SubscriptionState.EXPIRED.value, then=2),
            When(state=SubscriptionState.ACTIVE.value, then=3),
        ),
        "-price"
    )

    # Assert
    for expected_subscription, subscription in zip(
        qs, [subscription3, subscription5, subscription4, subscription1, subscription2]
    ):
        assert expected_subscription.uuid == subscription.uuid


@pytest.mark.django_db
def test_total_subscriptions_price_for_abc_com(
    organization_factory, user_factory, subscription_factory
):
    """
    Calculate total active subscriptions price per organization owner domain abc.com.
    """

    # Arrange
    subscription_factory.create(
        organization=organization_factory.create(
            owner=user_factory.create(email="user1@abc.com").uuid
        ),
        state=SubscriptionState.ACTIVE.value,
        price=100,
    )
    subscription_factory.create(
        organization=organization_factory.create(
            owner=user_factory.create(email="user2@abc.com").uuid
        ),
        state=SubscriptionState.ACTIVE.value,
        price=20,
    )
    subscription_factory.create(
        organization=organization_factory.create(
            owner=user_factory.create(email="user3@example.com").uuid
        ),
        state=SubscriptionState.ACTIVE.value,
        price=200,
    )
    subscription_factory.create(
        organization=organization_factory.create(
            owner=user_factory.create(email="user@google.com").uuid
        ),
        state=SubscriptionState.ACTIVE.value,
        price=231,
    )
    subscription_factory.create(
        organization=organization_factory.create(
            owner=user_factory.create(email="user4@abc.com").uuid
        ),
        state=SubscriptionState.EXPIRED.value,
        price=310,
    )
    subscription_factory.create(
        organization=organization_factory.create(
            owner=user_factory.create(email="user5@abc.com").uuid
        ),
        state=SubscriptionState.CANCELLED.value,
        price=12,
    )

    """
    Calculate total active subscriptions price per organization owner domain abc.com.""
    """
    domain = "@ABC.com"
    # Act
    qs = Subscription.objects.filter(
        state=SubscriptionState.ACTIVE.value,
        organization__owner__in=User.objects.filter(email__iendswith=domain).values_list("uuid", flat=True)
    ).aggregate(Sum("price"))

    # Assert
    assert qs["price__sum"] == 120.00


@pytest.mark.django_db
def test_subscriptions_discount(
    organization_factory, user_factory, subscription_factory
):
    """
    Calculate subscription discount on database level.
    discount = price - quantity * 10
    if discount > 50 => discount=50
    """

    # Arrange
    owner1, owner2, owner3, owner4, owner5, owner6 = user_factory.create_batch(6)

    subscription1 = subscription_factory.create(
        organization=organization_factory.create(owner=owner1.uuid),
        state=SubscriptionState.ACTIVE.value,
        price=100,
        quantity=2,
    )
    subscription2 = subscription_factory.create(
        organization=organization_factory.create(owner=owner2.uuid),
        state=SubscriptionState.ACTIVE.value,
        price=20,
        quantity=1,
    )
    subscription3 = subscription_factory.create(
        organization=organization_factory.create(owner=owner3.uuid),
        state=SubscriptionState.ACTIVE.value,
        price=200,
        quantity=10,
    )
    subscription4 = subscription_factory.create(
        organization=organization_factory.create(owner=owner4.uuid),
        state=SubscriptionState.ACTIVE.value,
        price=32,
        quantity=2,
    )
    subscription_factory.create(
        organization=organization_factory.create(owner=owner5.uuid),
        state=SubscriptionState.EXPIRED.value,
        price=310,
    )
    subscription_factory.create(
        organization=organization_factory.create(owner=owner6.uuid),
        state=SubscriptionState.CANCELLED.value,
        price=12,
    )

    """
    Calculate subscription discount on database level.
    discount = price - quantity * 10
    if discount > 50 => discount=50 
    """
    # Act
    qs = Subscription.objects.annotate(
        pre_discount=(
                F("price") - (F("quantity") * 10)
        ),
        discount=Case(
            When(Q(pre_discount__gte=50), then=Value(50)),
            default=F("pre_discount"),
            output_field=DecimalField(),
        )
    )

    # Assert
    assert qs[0].uuid == subscription1.uuid
    assert qs[0].discount == 50

    assert qs[1].uuid == subscription2.uuid
    assert qs[1].discount == 10

    assert qs[2].uuid == subscription3.uuid
    assert qs[2].discount == 50

    assert qs[3].uuid == subscription4.uuid
    assert qs[3].discount == 12
