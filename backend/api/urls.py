from django.urls import include, path, re_path
from rest_framework import routers

from .views import (
    FavoriteAPIView,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

app_name = "api"

router = routers.SimpleRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
    re_path(
        r"^recipes/(?P<recipe_id>\d+)/favorite/$",
        FavoriteAPIView.as_view(),
        name="favorite",
    ),
]
