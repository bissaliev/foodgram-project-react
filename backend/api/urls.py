from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    ShoppingCartDownloadAPIView,
)

app_name = "api"

router = routers.SimpleRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        ShoppingCartDownloadAPIView.as_view(),
        name="download_shop_list",
    ),
    path("", include(router.urls)),
]
