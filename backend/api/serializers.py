from recipes.models import Ingredient, Recipe, Tag
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения рецептов. """
    tag = serializers.SlugRelatedField(
        slug_field='slug', queryset=Tag.objects.all()
    )
    ingredient = serializers.SlugRelatedField(
        slug_field='name', many=True, queryset=Ingredient.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Recipe


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения тегов. """
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения ингредиентов. """
    class Meta:
        fields = '__all__'
        model = Ingredient
