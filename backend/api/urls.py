from django.urls import include, path
from rest_framework import routers

from .views.recipe_views import (
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartDownloadAPIView,
    TagViewSet,
)
from api.views.user_views import CustomUserViewSet

app_name = "api"

router = routers.SimpleRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        ShoppingCartDownloadAPIView.as_view(),
        name="download_shop_list",
    ),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
