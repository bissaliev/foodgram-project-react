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
    # authentication
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]

# endpoints
# /users/ list | create
# /users/{id}/ profile
# /users/me/ current user
# /users/resend_activation/
# /users/set_password/ change password
# /users/reset_password/
# /users/reset_password_confirm/
# /users/set_username/
# /users/reset_username/
# /users/reset_username_confirm/
# /token/login/ (Token Based Authentication) get token
# /token/logout/ (Token Based Authentication) delete token
