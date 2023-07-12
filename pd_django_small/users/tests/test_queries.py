import pytest
import random

from pd_django_small.users.models import User, AccountType


@pytest.mark.django_db
def test_user_corrupted_information(user_factory):
    """
    Some users data is corrupted, select all users where user last_name==email or first_name=email (case-insensitive),
    with 'BUSINESS' account type ordered by created_at desc.
    """

    # Arrange
    user_factory.create_batch(4)
    user_factory.create(
        first_name="Personal@example.com",
        email="personal@example.com",
        account_type=AccountType.PERSONAL.value,
    )
    user1 = user_factory.create(
        first_name="admin@example.com",
        email="admin@Example.com",
        account_type=AccountType.BUSINESS.value,
    )
    user2 = user_factory.create(
        last_name="Member@example.com",
        email="member@example.com",
        account_type=AccountType.BUSINESS.value,
    )
    user3 = user_factory.create(
        first_name="user@example.com",
        email="user@example.com",
        account_type=AccountType.BUSINESS.value,
    )

    # Act
    qs = None

    # Assert
    for expected_user, user in zip(qs, [user3, user2, user1]):
        assert expected_user.uuid == user.uuid


@pytest.mark.django_db
def test_users_bulk_create_or_update(faker, user_factory):
    """
    Create user for each email from "emails", if user with this email already exists
    then set user.is_active=True, user.is_removed=False (do not use factories!)
    use some fake information for "username" or just insert email value into this field.
    """

    # Arrange
    emails = [faker.email() for _ in range(250)]
    for email in random.sample(emails, 25):
        user_factory.create(email=email)

    # Act


@pytest.mark.django_db
def test_user_update_or_create(user_factory):
    """
    Create or update user with email "admin@example.com",
    if user exists than set user.is_active=True, user.is_removed=False.
    """

    # Arrange
    email = "admin@example.com"
    first_name = "John"
    last_name = "Doe"
    user_factory.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=False,
        is_removed=True,
    )

    # Act

    # Assert
    assert created is False
    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.is_active is True
    assert user.is_removed is False
