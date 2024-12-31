import weasyprint
from django.conf import settings
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..filters import RecipeFilter, SearchIngredientsFilter
from ..paginators import CustomPaginator
from ..serializers.recipe_serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    ShoppingSerializer,
    TagSerializer,
)
from api.permissions import IsAuthorOrReadOnly
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

    def get_queryset(self):
        queryset = super().get_queryset()
        # queryset = queryset.annotate()
        if self.request.user.is_authenticated:
            is_in_shopping_cart_subquery = Exists(
                ShoppingCart.objects.filter(
                    recipe_id=OuterRef("id"), user=self.request.user
                )
            )
            queryset = queryset.annotate(
                is_in_shopping_cart=is_in_shopping_cart_subquery
            )
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        recipe_id=OuterRef("id"), user=self.request.user
                    )
                )
            )
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("recipe_ingredients", "tags")
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return self.serializer_class

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Избранные рецепты."""
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={"recipe": recipe.id, "user": user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Favorite, recipe=recipe, user=user).delete()
        return Response(
            {"message": "Рецепт удален из избранных"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Список покупок."""
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            serializer = ShoppingSerializer(
                data={"recipe": recipe.id, "user": user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(ShoppingCart, recipe=recipe, user=user).delete()
        return Response(
            {"message": "Рецепт удален из списка покупок"},
            status=status.HTTP_204_NO_CONTENT,
        )


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


class ShoppingCartDownloadAPIView(APIView):
    """Скачать список покупок."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ingredients = (
            IngredientRecipe.objects.filter(
                recipe__shopping__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(sum_amount=Sum("amount"))
        )
        html = render_to_string(
            "shopping_cart.html", {"ingredients": ingredients}
        )
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=shortlist.pdf"
        weasyprint.HTML(string=html).write_pdf(
            response,
            stylesheets=[
                weasyprint.CSS(f"{settings.STATICFILES_DIRS[0]}/css/pdf.css")
            ],
        )
        return response
