import pytest
from django.urls import reverse

from recipes.models import Tag


@pytest.mark.django_db
class TestTag:
    """Тест тегов"""

    reverse_name_list = "api:tags-list"
    reverse_name_detail = "api:tags-detail"

    def test_tags_list(self, client, tag):
        url = reverse(self.reverse_name_list)
        response = client.get(url)
        assert (
            response.status_code == 200
        ), f"Метод GET на эндпоинт {url} должен возвращать статус ответа 200"
        assert isinstance(
            response.data, list
        ), "Запрос должен возвращать список"
        self.check_tags_results(response.data[0], tag)

    def test_tags_detail(self, client, tag):
        url = reverse(self.reverse_name_detail, args=[tag.id])
        response = client.get(url)
        assert (
            response.status_code == 200
        ), f"Метод GET на эндпоинт {url} должен возвращать статус ответа 200"
        assert isinstance(
            response.data, dict
        ), "Запрос должен возвращать словарь"
        self.check_tags_results(response.data, tag)

    def check_tags_results(self, result: dict, tag: Tag):
        for field, value in result.items():
            assert value == getattr(
                tag, field
            ), f"Значение поля {field} отображается некорректно"
