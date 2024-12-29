from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель Тегов."""

    name = models.CharField(
        max_length=200, unique=True, verbose_name="Название тега"
    )
    color = models.CharField(max_length=7, unique=True, verbose_name="Цвет")
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="Идентификатор"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиентов."""

    name = models.CharField(
        max_length=200, verbose_name="Название Ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}."


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name="Описание рецепта")
    image = models.ImageField(
        upload_to="recipes/images",
        null=True,
        blank=True,
        verbose_name="Изображение",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(1, "Нужно указать время приготовления!")
        ],
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Теги"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        verbose_name="Ингредиенты в рецепте",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель Ингредиент - Рецепт."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Ингредиенты",
        related_name="ingredient_recipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Рецепт",
        related_name="recipe_ingredients",
    )
    amount = models.IntegerField(
        default=1,
        verbose_name="Количество ингредиентов",
        validators=[
            MinValueValidator(
                1, "Количество ингредиентов должно быть не менее 1!"
            )
        ],
    )

    class Meta:
        verbose_name = "Ингредиент - Рецепт"
        verbose_name_plural = "Ингредиенты - Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="ingredient_recipe"
            )
        ]

    def __str__(self):
        return f"{self.recipe}: {self.amount} {self.ingredient}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_favorite",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ["user"]
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe"
            ),
        )

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        ordering = ["-id"]
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unique_recipe_shopping",
            ),
        )
