import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestIngredient:
    """Тест ингредиентов"""

    reverse_name_list = "api:ingredients-list"
    reverse_name_detail = "api:ingredients-detail"

    def test_ingredients_list(self, client, ingredient):
        url = reverse(self.reverse_name_list)
        response = client.get(url)
        assert (
            response.status_code == 200
        ), f"Метод GET на эндпоинт {url} должен возвращать статус ответа 200"
        assert isinstance(
            response.data, list
        ), "Запрос должен возвращать список"
        self.check_ingredient_result(response.data[0], ingredient)

    def test_ingredients_detail(self, client, ingredient):
        url = reverse(self.reverse_name_detail, args=[ingredient.id])
        response = client.get(url)
        assert (
            response.status_code == 200
        ), f"Метод GET на эндпоинт {url} должен возвращать статус ответа 200"
        assert isinstance(
            response.data, dict
        ), "Запрос должен возвращать словарь"
        self.check_ingredient_result(response.data, ingredient)

    def check_ingredient_result(self, result, ingredient):
        for field, value in result.items():
            assert value == getattr(
                ingredient, field
            ), f"Значение поля {field} отображается некорректно"
