from django_filters import rest_framework as filter
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class RecipeFilter(filter.FilterSet):
    author = filter.ModelChoiceFilter(
        queryset=User.objects.all(),
        to_field_name="email",
    )
    tags = filter.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = filter.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filter.BooleanFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset.exclude(in_favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset.exclude(shopping__user=self.request.user)


class SearchIngredientsFilter(SearchFilter):
    search_param = "name"

    class Meta:
        model = Ingredient
        fields = ("name",)
