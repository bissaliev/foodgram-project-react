import pytest
from django.urls import reverse

from users.models import Subscribe


@pytest.mark.django_db
class TestSubscription:
    """Тестирование подписок"""

    reverse_name_subscribe = "api:users-subscribe"
    reverse_name_subscriptions = "api:users-subscriptions"

    def test_subscribe_for_auth_user(self, auth_client, creator):
        url = reverse(self.reverse_name_subscribe, args=[creator.id])
        response = auth_client.post(url)
        assert response.status_code == 201

        response = auth_client.delete(url)
        assert response.status_code == 204

    def test_subscribe_for_not_auth_user(self, client, creator):
        url = reverse(self.reverse_name_subscribe, args=[creator.id])
        response = client.post(url)
        assert response.status_code == 401

        response = client.delete(url)
        assert response.status_code == 401

    def test_subscriptions_for_auth_user(
        self, auth_client, authorized_user, creator, recipe
    ):
        subscription_db = Subscribe.objects.create(
            author=creator, subscriber=authorized_user
        )
        url = reverse(self.reverse_name_subscriptions)
        response = auth_client.get(url)
        assert response.status_code == 200

        assert "results" in response.data
        subscription = response.data["results"][0]
        assert subscription_db.author.id == subscription.get("id")
        assert subscription_db.author.username == subscription.get("username")
        assert isinstance(subscription.get("recipes"), list)
        assert len(subscription.get("recipes")) == 1
        assert recipe.id == subscription.get("recipes")[0]["id"]
        assert "is_subscribed" in response.data["results"][0]
        assert response.data["results"][0]["is_subscribed"]
        assert "recipes_count" in response.data["results"][0]
        assert response.data["results"][0]["recipes_count"] == 1

    def test_subscriptions_for_not_auth_user(self, client):
        url = reverse(self.reverse_name_subscriptions)
        response = client.get(url)
        assert response.status_code == 401

    def test_is_subscribed_response(
        self, auth_client, authorized_user, creator
    ):
        response = auth_client.get(reverse("api:users-list"))
        assert response.status_code == 200
        assert "results" in response.data
        user_from_response = [
            user
            for user in response.data["results"]
            if user["id"] == creator.id
        ][0]
        assert "is_subscribed" in user_from_response
        assert not user_from_response["is_subscribed"]

        response = auth_client.get(
            reverse("api:users-detail", args=[creator.id])
        )
        assert response.status_code == 200
        assert "is_subscribed" in response.data
        assert not response.data["is_subscribed"]

        Subscribe.objects.create(author=creator, subscriber=authorized_user)

        response = auth_client.get(reverse("api:users-list"))
        assert response.status_code == 200
        user_from_response = [
            user
            for user in response.data["results"]
            if user["id"] == creator.id
        ][0]
        assert user_from_response["is_subscribed"]

        response = auth_client.get(
            reverse("api:users-detail", args=[creator.id])
        )
        assert response.status_code == 200
        assert "is_subscribed" in response.data
        assert response.data["is_subscribed"]
