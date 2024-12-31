import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from tests.utils import parse_uid_and_token

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

    user_list_url = reverse("api:users-list")
    reverse_name_user_detail = "api:users-detail"

    @pytest.mark.parametrize(
        "check_field",
        ("email", "username", "first_name", "last_name", "password"),
    )
    def test_register_user_with_invalid_data(
        self, check_field, registration_data, client
    ):
        registration_data.pop(check_field)
        response = client.post(
            self.register_url, data=registration_data, format="json"
        )
        assert response.status_code == 400

    def test_register_and_activate_user(self, client, registration_data):
        # Регистрация пользователя
        response = client.post(
            self.register_url, data=registration_data, format="json"
        )
        assert response.status_code == 201

        assert User.objects.filter(email=registration_data["email"]).exists()

        new_user = User.objects.filter(
            email=registration_data["email"]
        ).first()
        assert not new_user.is_active

        # Проверка, что email был отправлен
        assert len(mail.outbox) == 1
        body_email = mail.outbox[0].body
        parse_data = parse_uid_and_token(body_email)
        assert parse_data is not None

        # Активация пользователя
        mail.outbox = []
        activation_response = client.post(self.activate_url, data=parse_data)
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
        body_email = mail.outbox[0].body
        parse_data = parse_uid_and_token(body_email)
        assert parse_data is not None

        # Активация пользователя
        mail.outbox = []
        activation_response = client.post(self.activate_url, data=parse_data)
        assert activation_response.status_code == 204
        user.refresh_from_db()
        assert user.is_active
        assert len(mail.outbox) == 1

    def test_reset_email(self, client, authorized_user):
        response = client.post(
            self.reset_email_url, data={"email": authorized_user.email}
        )
        assert response.status_code == 204
        assert len(mail.outbox) == 1
        body_email = mail.outbox[0].body
        parse_data = parse_uid_and_token(body_email)
        assert parse_data is not None
        new_email = "update_email@example.com"
        data = {"new_email": new_email}
        data.update(parse_data)
        response = client.post(
            self.reset_email_confirm_url,
            data=data,
        )
        assert response.status_code == 204
        authorized_user.refresh_from_db()
        assert authorized_user.email == new_email

    def test_reset_password(self, client, authorized_user):
        response = client.post(
            self.reset_password_url, data={"email": authorized_user.email}
        )
        assert response.status_code == 204
        assert len(mail.outbox) == 1
        body_email = mail.outbox[0].body
        parse_data = parse_uid_and_token(body_email)
        assert parse_data is not None
        new_password = "NewPassword98!"
        data = {"new_password": new_password, **parse_data}
        response = client.post(self.reset_password_confirm_url, data=data)
        assert response.status_code == 204
        authorized_user.refresh_from_db()
        assert authorized_user.check_password(new_password)

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

    def test_user_list(self, client, authorized_user):
        response = client.get(self.user_list_url)
        assert response.status_code == 200
        assert "results" in response.data
        assert len(response.data["results"]) == 1
        assert isinstance(response.data["results"], list)
        user_from_response = response.data["results"][0]
        assert isinstance(user_from_response, dict)
        self.check_results_users(user_from_response, authorized_user)

    def test_user_retrieve(self, client, authorized_user):
        url = reverse(self.reverse_name_user_detail, args=[authorized_user.id])
        response = client.get(url)
        assert response.status_code == 200
        self.check_results_users(response.data, authorized_user)

    def check_results_users(self, response_user, user):
        is_subscribed = response_user.pop("is_subscribed", None)
        assert is_subscribed is not None
        for field, value in response_user.items():
            assert value == getattr(user, field)

    def test_user_update(
        self, auth_client, registration_data, authorized_user
    ):
        registration_data.pop("password")
        response = auth_client.put(
            reverse(self.reverse_name_user_detail, args=[authorized_user.id]),
            data=registration_data,
        )
        assert response.status_code == 200
        authorized_user.refresh_from_db()
        for field, value in registration_data.items():
            assert value == getattr(authorized_user, field)

    @pytest.mark.parametrize(
        "exclude_field", ("email", "username", "first_name", "last_name")
    )
    def test_user_update_with_invalid_data(
        self, auth_client, registration_data, authorized_user, exclude_field
    ):
        registration_data.pop("password")
        registration_data.pop(exclude_field)
        response = auth_client.put(
            reverse(self.reverse_name_user_detail, args=[authorized_user.id]),
            data=registration_data,
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "update_field, invalid_value",
        (
            ("email", "invalid"),
            ("username", ""),
            ("first_name", ""),
            ("last_name", ""),
        ),
    )
    def test_user_partial_update_with_invalid_data(
        self,
        auth_client,
        registration_data,
        authorized_user,
        update_field,
        invalid_value,
    ):
        registration_data.pop("password")
        registration_data[update_field] = invalid_value
        response = auth_client.patch(
            reverse(self.reverse_name_user_detail, args=[authorized_user.id]),
            data=registration_data,
        )
        assert response.status_code == 400

    def test_user_destroy(self, auth_client, authorized_user):
        current_password = "TestPass1234"
        authorized_user.set_password(current_password)
        authorized_user.save()
        url = reverse(self.reverse_name_user_detail, args=[authorized_user.id])
        response = auth_client.delete(
            url, {"current_password": current_password}
        )
        assert response.status_code == 204
        assert User.objects.count() == 0

    def test_user_destroy_with_invalid_data(
        self, auth_client, authorized_user
    ):
        current_password = "TestPass1234"
        authorized_user.set_password(current_password)
        authorized_user.save()
        url = reverse(self.reverse_name_user_detail, args=[authorized_user.id])
        response = auth_client.delete(
            url, {"current_password": current_password + "invalid"}
        )
        assert response.status_code == 400
