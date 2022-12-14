from recipes.models import Ingredient, Recipe, Tag
from rest_framework import viewsets

from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ Класс представления рецептов. """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


# поменять на ReadOnlyModelViewSet
class TagViewSet(viewsets.ModelViewSet):
    """ Класс представления тегов. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# поменять на ReadOnlyModelViewSet
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
