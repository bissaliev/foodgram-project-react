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
        assert "recipes_count" in response.data["results"][0]
        assert response.data["results"][0]["recipes_count"] == 1

    def test_subscriptions_for_not_auth_user(self, client):
        url = reverse(self.reverse_name_subscriptions)
        response = client.get(url)
        assert response.status_code == 401
