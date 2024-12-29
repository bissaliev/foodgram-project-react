import shutil
import tempfile

import pytest

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",  # Используем базу данных в памяти для ускорения тестов
        }
    }


@pytest.fixture(autouse=True)
def temp_media_root(settings):
    temp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir)


# ========= Users =======================================


@pytest.fixture
def authorized_user(django_user_model):
    return django_user_model.objects.create(email="user@mail.com")


@pytest.fixture
def creator(django_user_model):
    return django_user_model.objects.create(email="creator@mail.com")


@pytest.fixture
def auth_client(authorized_user):
    from rest_framework.authtoken.models import Token
    from rest_framework.test import APIClient

    client = APIClient()
    token = Token.objects.create(user=authorized_user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    return client


@pytest.fixture
def creator_client(creator):
    from rest_framework.authtoken.models import Token
    from rest_framework.test import APIClient

    client = APIClient()
    token = Token.objects.create(user=creator)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    return client


# ================= Recipes =========================


@pytest.fixture
def ingredient():
    data = {
        "name": "orange",
        "measurement_unit": "kg",
    }
    return Ingredient.objects.create(**data)


@pytest.fixture
def tag():
    data = {
        "name": "test tag",
        "color": "#efefef",
        "slug": "test_tag",
    }
    return Tag.objects.create(**data)


@pytest.fixture
def recipes_image():
    import base64
    from io import BytesIO

    from PIL import Image

    image = Image.new("RGB", size=(100, 100), color="red")
    image_io = BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)
    image_base64 = base64.b64encode(image_io.read()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"


@pytest.fixture
def recipe(creator, tag, ingredient, recipes_image):
    data = {
        "name": "test recipe",
        "author": creator,
        "text": "test text",
        "cooking_time": 1,
        "image": recipes_image,
    }
    recipe = Recipe.objects.create(**data)
    recipe.tags.add(tag)
    recipe.save()
    IngredientRecipe.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=5,  # Укажите значение для количества ингредиента
    )
    return recipe


@pytest.fixture
def recipe_data(ingredient, tag, recipes_image):
    return {
        "ingredients": [{"id": ingredient.id, "amount": 5}],
        "tags": [tag.id],
        "image": recipes_image,
        "name": "new recipe",
        "text": "new text",
        "cooking_time": 15,
    }
