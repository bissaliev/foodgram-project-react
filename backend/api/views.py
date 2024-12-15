from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter, SearchIngredientsFilter
from .paginators import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteShoppingSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс представления рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = CustomPaginator
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return self.serializer_class

    @staticmethod
    def __func_post_delete(model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            model.objects.get_or_create(user=user, recipe=recipe)
            serializer = FavoriteShoppingSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self.__func_post_delete(ShoppingCart, request, pk)

    @action(
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredient_list = "Cписок покупок:"
        ingredients = (
            IngredientRecipe.objects.filter(
                recipe__shopping__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(sum_amount=Sum("amount"))
        )
        for num, i in enumerate(ingredients):
            ingredient_list += (
                f'\n{i["ingredient__name"]} - '
                f'{i["sum_amount"]} {i["ingredient__measurement_unit"]}'
            )
            if num < ingredients.count() - 1:
                ingredient_list += ", "
        file = "shopping_list"
        response = HttpResponse(
            ingredient_list, "Content-Type: application/pdf"
        )
        response["Content-Disposition"] = f'attachment; filename="{file}.pdf"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс представления тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс представления ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchIngredientsFilter,)
    search_fields = ("^name",)


class FavoriteAPIView(APIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteShoppingSerializer

    def post(self, request, recipe_id: int):
        recipe = Recipe.objects.get(id=recipe_id)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(self.serializer_class(recipe).data)

    def delete(self, request, recipe_id: int):
        recipe = Recipe.objects.get(id=recipe_id)
        Favorite.objects.filter(recipe=recipe, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
