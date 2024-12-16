from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.serializers.user_serializers import CustomUserSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов с ингредиентами."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецептов."""

    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(many=True, source="recipe")
    is_favorited = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj) -> bool:
        """Находится ли рецепт в избранных."""
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe_id=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Находится ли рецепт в списках покупок."""
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe_id=obj).exists()
        )


# =============== Create Recipe ===============================


class IngredientRecipeCreateSerializer(serializers.Serializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "Количество ингредиента должно быть не менее 1."
        },
    )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value: list[dict[str, int]]):
        ingredient_ids = set()
        for ingredient in value:
            if ingredient["id"] in ingredient_ids:
                raise serializers.ValidationError(
                    "У рецепта не может быть два одинаковых ингредиента!"
                )
            ingredient_ids.add(ingredient["id"])
        return value

    @staticmethod
    def create_ingredients(
        ingredients: list[dict[str:int]], recipe: Recipe
    ) -> None:
        """Добавление ингредиентов в рецепт."""
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in ingredients
        )

    def create(self, validated_data: dict):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


# =============== Create Recipe ===============================^


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов и списка покупок."""

    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("recipe", "user")


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="recipe.id", read_only=True)
    name = serializers.ReadOnlyField(source="recipe.name")
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    image = Base64ImageField(read_only=True, source="recipe.image")

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time", "recipe", "user")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["recipe", "user"],
                message="Рецепт уже находится в избранных",
            )
        ]
        extra_kwargs = {
            "recipe": {"write_only": True},
            "user": {"write_only": True},
        }


class ShoppingSerializer(FavoriteSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time", "recipe", "user")
        extra_kwargs = {
            "recipe": {"write_only": True},
            "user": {"write_only": True},
        }
