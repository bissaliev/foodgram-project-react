from io import BytesIO

import pytest
from django.urls import reverse
from PyPDF2 import PdfReader
from rest_framework.test import APIClient

from recipes.models import Favorite, Recipe, ShoppingCart


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

    def test_recipe_retrieve(self, client: APIClient, recipe):
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


@pytest.mark.django_db
class TestShoppingCart:
    """Тест списка покупок"""

    reverse_name = "api:recipes-shopping-cart"
    reverse_name_download = "api:download_shop_list"

    def test_add_delete_to_favorite(
        self, auth_client, recipe, authorized_user
    ):
        url = reverse(self.reverse_name, args=[recipe.id])
        response = auth_client.post(url)
        assert (
            response.status_code == 201
        ), f"Метод POST на эндпоинт {url} должен возвращать статус ответа 201"
        assert (
            ShoppingCart.objects.filter(
                recipe=recipe, user=authorized_user
            ).exists()
        ), f"Метод POST на эндпоинт {url} некорректно сохраняет изменения в БД"
        response = auth_client.delete(url)
        assert response.status_code == 204, (
            f"Метод DELETE на эндпоинт {url} должен возвращать "
            "статус ответа 204"
        )
        assert (
            ShoppingCart.objects.filter(
                recipe=recipe, user=authorized_user
            ).count()
            == 0
        ), (
            f"Метод DELETE на эндпоинт {url} некорректно сохраняет"
            " изменения в БД"
        )

    @pytest.mark.parametrize("method", ("post", "delete"))
    def test_favorite_for_not_auth_user(self, method, client, recipe):
        url = reverse(self.reverse_name, args=[recipe.id])
        response = getattr(client, method)(url)
        assert response.status_code == 401, (
            "Анонимному пользователю не доступно добавление|удаление "
            "списка покупок."
        )

    def test_download_shopping_cart_not_auth_user(self, recipe, client):
        url = reverse(self.reverse_name_download)
        response = client.get(url)
        assert (
            response.status_code == 401
        ), "Анонимному пользователю не доступно скачивание списка покупок."

    def test_download_shopping_cart(self, recipe, auth_client):
        url = reverse(self.reverse_name, args=[recipe.id])
        response = auth_client.post(url)
        assert response.status_code == 201
        url = reverse(self.reverse_name_download)
        response = auth_client.get(url)
        assert response.status_code == 200, (
            f"Метод GET на эндпоинт {url} должен возвращать "
            "статус ответа 200"
        )
        assert (
            response["Content-Type"] == "application/pdf"
        ), "Некорректно скачивается файл pdf для списка покупок"
        assert (
            "attachment; filename=shortlist.pdf"
            in response["Content-Disposition"]
        ), "Некорректный Content-Disposition при скачивании файла pdf"
        pdf_content = BytesIO(response.content)
        reader = PdfReader(pdf_content)
        page_text = reader.pages[0].extract_text()
        recipe_ingredient = recipe.recipe_ingredients.all()[0]
        assert recipe_ingredient.ingredient.name in page_text, (
            "Название ингредиента некорректно отображается в файле pdf "
            "списка покупок"
        )
        assert str(recipe_ingredient.amount) in page_text, (
            "Количество ингредиента некорректно отображается в файле pdf"
            " списка покупок"
        )
        assert recipe_ingredient.ingredient.measurement_unit in page_text, (
            "measurement_unit некорректно отображается в файле pdf "
            "списка покупок"
        )


@pytest.mark.django_db
class TestRecipeFilterResponse:
    """Тест фильтрации рецептов"""

    base_url = reverse("api:recipes-list")

    def test_filter_by_author(self, auth_client: APIClient, recipe):
        url = f"{self.base_url}?author={recipe.author.email}"
        response = auth_client.get(url)
        self.check_filters_result(response, recipe, url, "author")

    def check_filters_result(self, response, recipe, url, param):
        assert (
            response.status_code == 200
        ), f"Метод GET на эндпоинт {url} должен возвращать статус ответа 200"
        assert isinstance(
            response.data["results"], list
        ), "Значение results должно быть списком"
        assert len(response.data["results"]) == 1, (
            f"Фильтрация рецептов по параметру {param} возвращает "
            "неверное количество результатов"
        )
        assert (
            response.data["results"][0]["name"] == recipe.name
        ), f"Некорректная фильтрация рецептов по параметру {param}"

    def test_filter_by_tags(self, auth_client: APIClient, recipe):
        url = f"{self.base_url}?tags={recipe.tags.all()[0].slug}"
        response = auth_client.get(url)
        self.check_filters_result(response, recipe, url, "tags")

    def test_filter_by_is_favorited(self, auth_client: APIClient, recipe):
        auth_client.post(reverse("api:recipes-favorite", args=[recipe.id]))

        url = f"{self.base_url}?is_favorited="
        response = auth_client.get(url + "true")
        self.check_filters_result(
            response, recipe, url + "true", "is_favorited"
        )

        response = auth_client.get(url + "false")
        assert response.status_code == 200
        assert len(response.data["results"]) == 0

    def test_filter_by_is_in_shopping_cart(
        self, auth_client: APIClient, recipe
    ):
        auth_client.post(
            reverse("api:recipes-shopping-cart", args=[recipe.id])
        )
        url = f"{self.base_url}?is_in_shopping_cart="
        response = auth_client.get(url + "true")
        self.check_filters_result(
            response, recipe, url + "true", "is_in_shopping_cart"
        )

        response = auth_client.get(url + "false")
        assert response.status_code == 200, (
            f"Метод GET на эндпоинт {url}false должен возвращать "
            "статус ответа 200"
        )
        assert len(response.data["results"]) == 0, (
            "Фильтрация рецептов по параметру is_in_shopping_cart=false "
            "возвращает неверное количество результатов"
        )


@pytest.mark.django_db
class TestRecipePaginator:
    """Тестирование пагинации рецептов"""

    url = reverse("api:recipes-list")

    def test_recipes_pagination2(self, recipes_many_data: list, client):
        Recipe.objects.bulk_create(recipes_many_data)
        response = client.get(self.url)
        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert len(response.data["results"]) == 6
        assert response.data["count"] == 10
        assert response.data["next"] is not None
