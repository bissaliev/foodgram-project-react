from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from api.serializers.recipe_serializers import (
    FavoriteSerializer,
    ShoppingSerializer,
)
from api.serializers.user_serializers import SubscribeSerializer


# ==============RECIPE=====================
class RecipeViewSetExtension(OpenApiViewExtension):
    target_class = "api.views.recipe_views.RecipeViewSet"

    def view_replacement(self):
        from recipes.models import Recipe

        @extend_schema(tags=["Рецепты"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список рецептов",
                description=(
                    "Доступно любому неавторизованному пользователю. Доступна "
                    "фильтрация по избранному, автору, списку покупок и тегам."
                ),
                auth=[],
            ),
            create=extend_schema(
                summary="Создание рецепта",
                description="Доступно только авторизованному пользователю.",
            ),
            retrieve=extend_schema(
                summary="Получение рецепта",
                description=(
                    "Детальная информация о рецепте. Доступно любому "
                    "неавторизованному пользователю."
                ),
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
        )
        class Fixed(self.target_class):
            queryset = Recipe.objects.none()

            @extend_schema(
                methods=["post"],
                operation_id="favorite_create",
                summary="Добавление рецепта в избранные",
                description=(
                    "Управление списком избранных рецептов. "
                    "Доступно только авторизованному пользователю."
                ),
                tags=["Избранные рецепты"],
                request=None,
                responses={201: FavoriteSerializer},
            )
            @extend_schema(
                methods=["delete"],
                operation_id="favorite_destroy",
                summary="Удаление рецепта из избранных",
                description=(
                    "Управление списком избранных рецептов. "
                    "Доступно только авторизованному пользователю."
                ),
                tags=["Избранные рецепты"],
                responses={
                    204: OpenApiResponse(
                        description="Рецепт успешно удален из избранных",
                        examples=[{"message": "Рецепт удален из избранных"}],
                    )
                },
            )
            def favorite(self, request, *args, **kwargs):
                return super().favorite(request, *args, **kwargs)

            @extend_schema(
                methods=["post"],
                operation_id="shopping_cart_create",
                summary="Добавление рецепта в список покупок",
                description=(
                    "Управление списком избранных рецептов. "
                    "Доступно только авторизованному пользователю."
                ),
                tags=["Список покупок"],
                request=None,
                responses={201: ShoppingSerializer},
            )
            @extend_schema(
                methods=["delete"],
                operation_id="shopping_cart_destroy",
                summary="Удаление рецепта из списка покупок",
                description=(
                    "Управление списком покупок. "
                    "Доступно только авторизованному пользователю."
                ),
                tags=["Список покупок"],
            )
            def shopping_cart(self, request, *args, **kwargs):
                return super().shopping_cart(request, *args, **kwargs)

        return Fixed


class ShoppingCartDownloadAPIViewExtension(OpenApiViewExtension):
    target_class = "api.views.recipe_views.ShoppingCartDownloadAPIView"

    def view_replacement(self):
        from recipes.models import ShoppingCart

        @extend_schema(tags=["Список покупок"])
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

        @extend_schema(tags=["Теги"])
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

        @extend_schema(tags=["Ингредиенты"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список ингредиентов",
                description=(
                    "Список ингредиентов с возможностью поиска по имени. "
                    "Страница доступна всем пользователям."
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

        @extend_schema(tags=["Пользователи"])
        @extend_schema_view(
            list=extend_schema(
                summary="Список пользователей",
                description="Получение списка пользователей",
            ),
            create=extend_schema(
                summary="Регистрация пользователя",
                description="Регистрация нового пользователя.",
            ),
            retrieve=extend_schema(
                summary="Получение пользователя",
                description="Получение определенного пользователя по id",
            ),
            update=extend_schema(
                summary="Обновление данных пользователя",
                description="Обновление данных пользователя",
            ),
            partial_update=extend_schema(
                summary="Частичное обновление данных пользователя",
                description="Частичное обновление данных пользователя.",
            ),
            destroy=extend_schema(
                summary="Удаление пользователя",
                description="Удаление пользователя",
            ),
            # subscribe=extend_schema(
            #     methods=["post", "delete"],
            #     summary="Управление подписками",
            #     description="Управление подписками пользователем.",
            #     tags=["Подписки"],
            # ),
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
                description="Просмотр списка подписок пользователем.",
                tags=["Подписки"],
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
                description=(
                    "Для получения / обновления / удаления "
                    "аутентифицированного пользователя."
                ),
            ),
            activation=extend_schema(
                summary="Активация аккаунта",
                description=(
                    "Активации учётной записи пользователя. "
                    "`HTTP_403_FORBIDDEN` будет вызвано, если пользователь уже"
                    " активен при вызове этой конечной точки (это произойдёт,"
                    " если вы вызовете её более одного раза)."
                ),
            ),
            resend_activation=extend_schema(
                summary="Повторная активация аккаунта",
                description=(
                    "Пользователь повторно отправляет электронное письмо для "
                    "активации. Электронное письмо не будет отправлено, если "
                    "пользователь уже активен или если у него нет рабочего "
                    "пароля."
                ),
            ),
            set_username=extend_schema(
                summary="Установить новый `email`",
                description="Изменение `email` пользователя.",
            ),
            set_password=extend_schema(
                summary="Установить новый пароль",
                description="Изменение пароля пользователя.",
            ),
            reset_username=extend_schema(
                summary="Сброс `email`",
                description=(
                    "Отправка пользователю электронного письма со "
                    "ссылкой для сброса `email`."
                ),
            ),
            reset_username_confirm=extend_schema(
                summary="Подтверждение сброса email",
                description="Подтверждение процесса сброса email.",
            ),
            reset_password=extend_schema(
                summary="Сбросить пароль",
                description=(
                    "Отправка пользователю электронного письма со ссылкой "
                    "для сброса пароля."
                ),
            ),
            reset_password_confirm=extend_schema(
                summary="Подтверждение сброса пароля",
                description=("Подтверждение процесса сброса пароля."),
            ),
        )
        class Fixed(self.target_class):
            queryset = User.objects.none()

            @extend_schema(
                methods=["post"],
                summary="Добавление подписки",
                description="Пользователь подписывается на автора.",
                tags=["Подписки"],
                operation_id="subscribe_create",
                request=None,
                responses={201: SubscribeSerializer},
                # TODO: Доделать ответ для подписок при создании
            )
            @extend_schema(
                methods=["delete"],
                summary="Удаление подписки",
                description="Пользователь удаляет подписку на автора.",
                tags=["Подписки"],
                operation_id="subscribe_destroy",
            )
            def subscribe(self, request, *args, **kwargs):
                return super().subscribe(request, *args, **kwargs)

        return Fixed


# ==============USERS=====================
# ==============Authentication=====================


class TokenCreateViewExtension(OpenApiViewExtension):
    target_class = "djoser.views.TokenCreateView"

    def view_replacement(self):
        from rest_framework.authtoken.models import Token

        @extend_schema(tags=["Аутентификация"])
        @extend_schema_view(
            post=extend_schema(
                summary="Получение токена авторизации",
                description=(
                    "Этот эндпоинт используется для получения токена "
                    "авторизации. Передайте `email` и `password` в теле запроса."
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

        @extend_schema(tags=["Аутентификация"])
        @extend_schema_view(
            post=extend_schema(
                summary="Удаление токена авторизации",
                description=(
                    "Выхода пользователя из системы (удаления токена "
                    "аутентификации пользователя)"
                ),
            )
        )
        class Fixed(self.target_class):
            queryset = Token.objects.none()

        return Fixed


# ==============Authentication=====================
