from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .paginators import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Класс представления рецептов. """
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = CustomPaginator
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        detail=True, methods=['POST', 'DELETE'], url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """ Добавление или удаление рецепта из избранного. """
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredient_list = "Cписок покупок:"
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        for num, i in enumerate(ingredients):
            ingredient_list += (
                f'\n{i["ingredient__name"]} - '
                f'{i["amount"]} {i["ingredient__measurement_unit"]}'
            )
            if num < ingredients.count() - 1:
                ingredient_list += ', '
        file = 'shopping_list'
        response = HttpResponse(
            ingredient_list, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ Класс представления тегов. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ Класс представления ингредиентов. """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)
