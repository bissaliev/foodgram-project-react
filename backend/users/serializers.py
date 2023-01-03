from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Subscribe, User
from recipes.models import Recipe


class CustomUserSerializer(UserSerializer):
    """ Сериализатор кастомного пользователя. """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            subscriber=request.user, author=obj
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор для создания нового пользователя. """

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор для подписок. """
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'id', 'username', 'first_name',
            'last_name', 'recipes', 'is_subscribed', 'recipes_count'
        )

    def get_recipes(self, obj):
        """Отображает рецепты в мои подписки."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit:
            recipes = recipes.all()[:int(limit)]
        return SubscribeRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """ Количество рецептов данного автора. """
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        """ Подписан ли пользователь на данного автора. """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            subscriber=request.user, author=obj.author
        ).exists()
