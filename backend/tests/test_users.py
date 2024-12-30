import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.usefixtures("temp_email_backend")
class TestUser:
    register_url = reverse("api:users-list")
    activate_url = reverse("api:user-activation")
    reactivate_url = reverse("api:user-resend-activation")

    reset_email_url = reverse("api:user-reset-username")
    reset_email_confirm_url = reverse("api:user-reset-username-confirm")

    reset_password_url = reverse("api:user-reset-password")
    reset_password_confirm_url = reverse("api:user-reset-password-confirm")
    set_email_url = reverse("api:user-set-username")
    set_password_url = reverse("api:user-set-password")

    def test_register_user(self, client):
        data = {
            "email": "test@example.com",
            "username": "username",
            "first_name": "User",
            "last_name": "User",
            "password": "StrongPassword123!",
        }
        # Регистрация пользователя
        response = client.post(self.register_url, data=data, format="json")
        assert response.status_code == 201

        assert User.objects.filter(email="test@example.com").exists()

        new_user = User.objects.filter(email="test@example.com").first()
        assert not new_user.is_active

        # Проверка, что email был отправлен
        assert len(mail.outbox) == 1
        activation_email = mail.outbox[0]

        activation_link = re.search(
            r"https?://testserver/activate/(?P<uid>[A-Z]+)/(?P<token>[A-Za-z0-9-]+)/",
            activation_email.body,
        )
        assert activation_link is not None

        # Активация пользователя
        mail.outbox = []
        activation_response = client.post(
            self.activate_url, data=activation_link.groupdict()
        )
        assert activation_response.status_code == 204
        new_user.refresh_from_db()
        assert new_user.is_active
        assert len(mail.outbox) == 1

    def test_resend_activation_user(self, client):
        user = User.objects.create(email="resend@example.com", is_active=False)
        response = client.post(self.reactivate_url, data={"email": user.email})
        assert response.status_code == 204
        assert len(mail.outbox) == 1

        # Проверка, что email был отправлен
        assert len(mail.outbox) == 1
        activation_email = mail.outbox[0]

        activation_link = re.search(
            r"https?://testserver/activate/(?P<uid>[A-Z]+)/(?P<token>[A-Za-z0-9-]+)/",
            activation_email.body,
        )
        assert activation_link is not None

        # Активация пользователя
        mail.outbox = []
        activation_response = client.post(
            self.activate_url, data=activation_link.groupdict()
        )
        assert activation_response.status_code == 204
        user.refresh_from_db()
        assert user.is_active
        assert len(mail.outbox) == 1

    def test_reset_email(self, client):
        user = User.objects.create(email="reset_email@example.com")
        response = client.post(
            self.reset_email_url, data={"email": user.email}
        )
        assert response.status_code == 204
        assert len(mail.outbox) == 1
        body_email = mail.outbox[0].body
        link_confirm = re.search(
            r"https?://testserver/email-reset-confirm/(?P<uid>[A-Z]+)/(?P<token>[A-Za-z0-9-]+)/",
            body_email,
        )
        new_email = "update_email@example.com"
        data = {"new_email": new_email}
        data.update(link_confirm.groupdict())
        response = client.post(
            self.reset_email_confirm_url,
            data=data,
        )
        assert response.status_code == 204
        user.refresh_from_db()
        assert user.email == new_email

    def test_reset_password(self, client):
        user = User.objects.create(
            email="reset_email@example.com", password="Example1234!"
        )
        response = client.post(
            self.reset_password_url, data={"email": user.email}
        )
        assert response.status_code == 204
        assert len(mail.outbox) == 1
        body_email = mail.outbox[0].body
        link_from_email = re.search(
            r"https?://testserver/password-reset-confirm/(?P<uid>[A-Z]+)/(?P<token>[A-Za-z0-9-]+)/",
            body_email,
        )
        new_password = "NewPassword98!"
        data = {"new_password": new_password, **link_from_email.groupdict()}
        response = client.post(self.reset_password_confirm_url, data=data)
        assert response.status_code == 204
        user.refresh_from_db()
        assert user.check_password(new_password)

    def test_set_email(self, auth_client, authorized_user):
        current_password = "TestPass1234!"
        new_email = "new-test-email@example.com"
        authorized_user.set_password(current_password)
        authorized_user.save()
        data = {
            "current_password": current_password,
            "new_email": new_email,
        }
        response = auth_client.post(self.set_email_url, data=data)
        assert response.status_code == 204
        authorized_user.refresh_from_db()
        assert authorized_user.email == new_email

    def test_set_password(self, auth_client, authorized_user):
        current_password = "TestPass1234!"
        new_password = "NewTest5678!"
        authorized_user.set_password(current_password)
        authorized_user.save()
        data = {
            "new_password": new_password,
            "current_password": current_password,
        }
        response = auth_client.post(self.set_password_url, data=data)
        assert response.status_code == 204
        authorized_user.refresh_from_db()
        assert authorized_user.check_password(new_password)
