from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscribe, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания нового пользователя."""

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")


class RecipeForSubscribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = RecipeForSubscribeSerializer(
        many=True, source="author.recipes", read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField()

    class Meta:
        model = Subscribe
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "subscriber",
            "author",
            "is_subscribed",
            "recipes_count",
        )
        extra_kwargs = {
            "author": {"write_only": True},
            "subscriber": {"write_only": True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("author", "subscriber"),
                message="Вы уже подписаны на данного автора",
            )
        ]

    def validate(self, attrs):
        author = attrs["author"]
        subscriber = attrs["subscriber"]
        if author == subscriber:
            raise serializers.ValidationError(
                "Вы не можете подписаться на самого себя."
            )
        return super().validate(attrs)

    def get_is_subscribed(self, obj):
        """Подписан ли пользователь на данного автора."""
        user = self.context.get("request").user
        return user.is_authenticated and obj.subscriber_id == user.id

    def to_representation(self, instance):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        data = super().to_representation(instance)
        if limit and limit.isdigit():
            data["recipes"] = data["recipes"][: int(limit)]
        return data
