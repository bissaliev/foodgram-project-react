from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from api.serializers.user_serializers import SubscribeSerializer


# ==============RECIPE=====================
class RecipeViewSetExtension(OpenApiViewExtension):
    target_class = "api.views.recipe_views.RecipeViewSet"

    def view_replacement(self):
        from recipes.models import Recipe

        @extend_schema(tags=["RECIPES"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список рецептов",
                description=(
                    "Страница доступна всем пользователям. Доступна фильтрация"
                    " по избранному, автору, списку покупок и тегам."
                ),
                auth=[],
            ),
            create=extend_schema(
                summary="Создание рецепта",
                description="Доступно только авторизованному пользователю.",
            ),
            retrieve=extend_schema(
                summary="Получение рецепта",
                description="Детальная информация о рецепте.",
                auth=[],
            ),
            update=extend_schema(
                summary="Обновление рецепта",
                description="Доступно только автору данного рецепта.",
            ),
            partial_update=extend_schema(
                summary="Частичное обновление рецепта",
                description="Доступно только автору данного рецепта.",
            ),
            destroy=extend_schema(
                summary="Удаление рецепта",
                description="Доступно только автору данного рецепта.",
            ),
            favorite=extend_schema(
                methods=["post", "delete"],
                operation_id="favorite",
                summary="Избранные рецепты",
                description="Доступно только авторизованному пользователю.",
                tags=["FAVORITE"],
            ),
            shopping_cart=extend_schema(
                methods=["post", "delete"],
                summary="Список покупок",
                description="Доступно только авторизованному пользователю.",
                tags=["SHOPPING_CART"],
            ),
        )
        class Fixed(self.target_class):
            queryset = Recipe.objects.none()

        return Fixed


class ShoppingCartDownloadAPIViewExtension(OpenApiViewExtension):
    target_class = "api.views.recipe_views.ShoppingCartDownloadAPIView"

    def view_replacement(self):
        from recipes.models import ShoppingCart

        @extend_schema(tags=["SHOPPING_CART"])
        @extend_schema_view(
            get=extend_schema(
                summary="Скачать список покупок",
                description=(
                    "Скачать файл со списком покупок. "
                    "Доступно только авторизованным пользователям."
                ),
            ),
        )
        class Fixed(self.target_class):
            queryset = ShoppingCart.objects.none()

        return Fixed


class TagViewSetExtension(OpenApiViewExtension):
    target_class = "api.views.recipe_views.TagViewSet"

    def view_replacement(self):
        from recipes.models import Tag

        @extend_schema(tags=["TAGS"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список тегов",
                description="Страница доступна всем пользователям.",
            ),
            retrieve=extend_schema(
                summary="Получение тега",
                description="Страница доступна всем пользователям.",
            ),
        )
        class Fixed(self.target_class):
            queryset = Tag.objects.none()

        return Fixed


class IngredientViewSetExtension(OpenApiViewExtension):
    target_class = "api.views.recipe_views.IngredientViewSet"

    def view_replacement(self):
        from recipes.models import Ingredient

        @extend_schema(tags=["INGREDIENTS"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список ингредиентов",
                description=(
                    "Список ингредиентов с возможностью поиска по имени."
                ),
            ),
            retrieve=extend_schema(
                summary="Получение ингредиента",
                description="Страница доступна всем пользователям.",
            ),
        )
        class Fixed(self.target_class):
            queryset = Ingredient.objects.none()

        return Fixed


# ==============RECIPE=====================
# ==============USERS=====================
class CustomUserViewSetExtension(OpenApiViewExtension):
    target_class = "api.views.user_views.CustomUserViewSet"

    def view_replacement(self):
        from users.models import User

        @extend_schema(tags=["USERS"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список пользователей",
                description="",
            ),
            create=extend_schema(
                summary="Создание пользователя",
                description="Доступно только авторизованному пользователю.",
            ),
            retrieve=extend_schema(
                summary="Получение пользователя",
                description="",
            ),
            update=extend_schema(
                summary="Обновление данных пользователя",
                description="",
            ),
            partial_update=extend_schema(
                summary="Частичное обновление данных пользователя",
                description="Доступно только автору данного рецепта.",
            ),
            destroy=extend_schema(
                summary="Удаление пользователя",
                description="",
            ),
            subscribe=extend_schema(
                methods=["post", "delete"],
                summary="Управление подписками",
                description="",
                tags=["SUBSCRIPTION"],
            ),
            subscriptions=extend_schema(
                parameters=[
                    OpenApiParameter(
                        name="page",
                        type=int,
                        required=False,
                        description="Номер страницы.",
                    ),
                    OpenApiParameter(
                        name="limit",
                        type=int,
                        required=False,
                        description="Количество объектов на странице.",
                    ),
                    OpenApiParameter(
                        name="recipes_limit",
                        type=int,
                        required=False,
                        description="Количество объектов внутри поля recipes.",
                    ),
                ],
                summary="Список подписок",
                description="",
                tags=["SUBSCRIPTION"],
                responses={
                    200: inline_serializer(
                        name="PaginatedRecipeResponse",
                        fields={
                            "count": serializers.IntegerField(),
                            "next": serializers.URLField(allow_null=True),
                            "previous": serializers.URLField(allow_null=True),
                            "results": SubscribeSerializer(many=True),
                        },
                    )
                },
            ),
            me=extend_schema(
                summary="Управление профилем",
                description="",
            ),
            set_username=extend_schema(
                summary="Установка новый email",
                description="",
            ),
            set_password=extend_schema(
                summary="Установка новый пароль",
                description="",
            ),
            # исключенные эндпоинты
            reset_username=extend_schema(exclude=True),
            reset_username_confirm=extend_schema(exclude=True),
            reset_password=extend_schema(exclude=True),
            reset_password_confirm=extend_schema(exclude=True),
            activation=extend_schema(exclude=True),
            resend_activation=extend_schema(exclude=True),
        )
        class Fixed(self.target_class):
            queryset = User.objects.none()

        return Fixed


# ==============USERS=====================


class TokenCreateViewExtension(OpenApiViewExtension):
    target_class = "djoser.views.TokenCreateView"

    def view_replacement(self):
        from rest_framework.authtoken.models import Token

        @extend_schema(tags=["AUTH"])
        @extend_schema_view(
            post=extend_schema(
                summary="Получение токена авторизации",
                description=(
                    "Этот эндпоинт используется для получения токена авторизации. "
                    "Передайте email и password в теле запроса."
                ),
            )
        )
        class Fixed(self.target_class):
            queryset = Token.objects.none()

        return Fixed


class TokenDestroyViewExtension(OpenApiViewExtension):
    target_class = "djoser.views.TokenDestroyView"

    def view_replacement(self):
        from rest_framework.authtoken.models import Token

        @extend_schema(tags=["AUTH"])
        @extend_schema_view(
            post=extend_schema(
                summary="Удаление токена авторизации",
                description=(
                    "Список ингредиентов с возможностью поиска по имени."
                ),
            )
        )
        class Fixed(self.target_class):
            queryset = Token.objects.none()

        return Fixed
