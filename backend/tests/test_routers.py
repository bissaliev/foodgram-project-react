import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from recipes.models import Favorite, Recipe


@pytest.mark.django_db
class TestRecipe:
    """Тестирование Recipe"""

    recipe_list_url = "api:recipes-list"
    recipe_detail_url = "api:recipes-detail"

    def test_recipes_list(self, client, recipe):
        url = reverse(self.recipe_list_url)
        response = client.get(url)
        assert response.status_code == 200, "Статус ответа должен быть 200"
        assert "results" in response.data, "Отсутствует переменная results"
        recipes = response.data.get("results")
        assert isinstance(
            recipes, list
        ), "Переменная results должна быть списком"
        assert len(recipes) == 1, "Количество элементов в ответе неверное"
        self.check_results_recipes(recipes[0], recipe)

    def check_results_recipes(self, result, recipe):
        assert result.get("id") == recipe.id, "Поле id некорректно"

        # tags
        assert "tags" in result, "В ответе отсутствует поле tags"
        tags = result.get("tags")
        assert isinstance(tags, list), "Поле tags должна быть списком"
        assert isinstance(
            tags[0], dict
        ), "Поле tags должна содержать список словарей"
        tags_in_db = recipe.tags.all()[0]
        for field, value in tags[0].items():
            assert value == getattr(
                tags_in_db, field
            ), f"Некорректное отображение поля tags.{field}"

        # ingredients
        assert "ingredients" in result, "В ответе отсутствует поле ingredients"
        ingredients = result.get("ingredients")
        assert isinstance(
            ingredients, list
        ), "Поле ingredients должна быть списком"
        assert isinstance(
            ingredients[0], dict
        ), "Поле ingredients должна содержать список словарей"
        ingredient_in_db = recipe.ingredients.all()[0]
        for field, value in ingredients[0].items():
            if field != "amount":
                assert value == getattr(
                    ingredient_in_db, field
                ), f"Некорректное отображение поля ingredients.{field}"

        # author
        assert "author" in result, "В ответе отсутствует поле author"
        author = result.get("author")
        assert isinstance(author, dict)
        for field, value in author.items():
            assert value == getattr(
                recipe.author, field
            ), f"Некорректное отображение поля author.{field}"

        assert (
            "is_favorited" in result
        ), "В ответе отсутствует поле is_favorited"
        assert isinstance(
            result["is_favorited"], bool
        ), "Тип поля is_favorited должно быть bool"

        assert (
            "is_in_shopping_cart" in result
        ), "В ответе отсутствует поле is_in_shopping_cart"
        assert isinstance(
            result["is_in_shopping_cart"], bool
        ), "Тип поля is_in_shopping_cart должно быть bool"

        assert "name" in result, "В ответе отсутствует поле name"
        assert (
            result["name"] == recipe.name
        ), "Некорректное отображение поля name."

        assert "text" in result, "В ответе отсутствует поле text"
        assert (
            result["text"] == recipe.text
        ), "Некорректное отображение поля text."

        assert (
            "cooking_time" in result
        ), "В ответе отсутствует поле cooking_time"
        assert (
            result["cooking_time"] == recipe.cooking_time
        ), "Некорректное отображение поля cooking_time."

    def test_recipe_retrieve(self, client, recipe):
        url = reverse(self.recipe_detail_url, args=[recipe.id])
        response = client.get(url)
        assert response.status_code == 200, "Статус ответа должен быть 200"
        self.check_results_recipes(response.data, recipe)

    def test_create_recipe_for_auth_user(self, recipe_data, auth_client):
        url = reverse(self.recipe_list_url)
        response = auth_client.post(url, data=recipe_data, format="json")
        assert (
            response.status_code == 201
        ), "Авторизованному пользователю доступно создание рецептов"
        recipe = Recipe.objects.filter(name=recipe_data["name"]).first()
        self.check_results_recipes(response.data, recipe)

    def test_create_recipe_for_not_auth_user(self, recipe_data, client):
        url = reverse(self.recipe_list_url)
        response = client.post(url, data=recipe_data, format="json")
        assert (
            response.status_code == 401
        ), "Неавторизованному пользователю не доступно создание рецептов"

    def test_update_recipe_for_author(
        self, creator_client, recipe, recipe_data
    ):
        url = reverse(self.recipe_detail_url, args=[recipe.id])
        response = creator_client.put(url, data=recipe_data, format="json")
        assert (
            response.status_code == 200
        ), f"Статус ответа для метода PUT на {url} должен быть 200"
        recipe.refresh_from_db()
        self.check_results_recipes(response.data, recipe)

    def test_partial_update_recipe_for_author(
        self, creator_client, recipe, recipe_data
    ):
        url = reverse(self.recipe_detail_url, args=[recipe.id])
        response = creator_client.patch(url, data=recipe_data, format="json")
        assert (
            response.status_code == 200
        ), f"Статус ответа для метода PATCH на {url} должен быть 200"
        recipe.refresh_from_db()
        self.check_results_recipes(response.data, recipe)

    def test_delete_recipe_for_author(self, creator_client, recipe):
        url = reverse(self.recipe_detail_url, args=[recipe.id])
        response = creator_client.delete(url)
        assert (
            response.status_code == 204
        ), f"Статус ответа для метода DELETE на {url} должен быть 204"
        assert (
            Recipe.objects.count() == 0
        ), "Метод некорректно удаляет рецепт из БД"

    @pytest.mark.parametrize("method", ("put", "patch", "delete"))
    def test_accessibility_of_endpoint_to_not_author(
        self, auth_client: APIClient, recipe, recipe_data, method
    ):
        url = reverse(self.recipe_detail_url, args=[recipe.id])
        response = getattr(auth_client, method)(
            url, data=recipe_data, format="json"
        )
        assert (
            response.status_code == 403
        ), "Изменять рецепт может только автор"

    @pytest.mark.parametrize(
        "excluded_field",
        ("ingredients", "tags", "image", "name", "text", "cooking_time"),
    )
    def test_create_recipe_with_invalid_data(
        self, auth_client, recipe_data, excluded_field
    ):
        recipe_data.pop(excluded_field)
        url = reverse(self.recipe_list_url)
        response = auth_client.post(url, data=recipe_data, format="json")
        assert (
            response.status_code == 400
        ), f"Поле {excluded_field} должно быть обязательным"
        recipe_data[excluded_field] = False
        response = auth_client.post(url, data=recipe_data, format="json")
        assert (
            response.status_code == 400
        ), "Рецепт не создается с некорректными данными"

    @pytest.mark.parametrize(
        "excluded_field",
        ("ingredients", "tags", "image", "name", "text", "cooking_time"),
    )
    def test_create_recipe_with_invalid_data2(
        self, auth_client, recipe_data, excluded_field
    ):
        recipe_data.pop(excluded_field)
        url = reverse(self.recipe_list_url)
        response = auth_client.post(url, data=recipe_data, format="json")
        assert (
            response.status_code == 400
        ), f"Поле {excluded_field} должно быть обязательным"
        recipe_data[excluded_field] = False
        response = auth_client.post(url, data=recipe_data, format="json")
        assert (
            response.status_code == 400
        ), "Рецепт не создается с некорректными данными"

    @pytest.mark.parametrize("method", ("put", "patch"))
    @pytest.mark.parametrize(
        "invalid_field",
        ("ingredients", "tags", "image", "name", "text", "cooking_time"),
    )
    def test_update_recipe_with_invalid_data(
        self, invalid_field, method, creator_client, recipe, recipe_data
    ):
        url = reverse(self.recipe_detail_url, args=[recipe.id])
        recipe_data[invalid_field] = False
        response = getattr(creator_client, method)(
            url, data=recipe_data, format="json"
        )
        assert response.status_code == 400, (
            f"Метод {method.upper()} с некорректным значением поля"
            f" {invalid_field} возвращает статус 400"
        )


@pytest.mark.django_db
class TestFavorite:
    """Тест управления избранными рецептами"""

    def test_add_delete_to_favorite(
        self, auth_client, recipe, authorized_user
    ):
        url = reverse("api:recipes-favorite", args=[recipe.id])
        response = auth_client.post(url)
        assert response.status_code == 201
        assert Favorite.objects.filter(
            recipe=recipe, user=authorized_user
        ).exists()
        response = auth_client.delete(url)
        assert response.status_code == 204
        assert (
            Favorite.objects.filter(
                recipe=recipe, user=authorized_user
            ).count()
            == 0
        )

    @pytest.mark.parametrize("method", ("post", "delete"))
    def test_favorite_for_not_auth_user(self, method, client, recipe):
        url = reverse("api:recipes-favorite", args=[recipe.id])
        response = getattr(client, method)(url)
        assert response.status_code == 401, (
            "Анонимному пользователю не доступно добавление|удаление "
            "избранных рецептов."
        )
