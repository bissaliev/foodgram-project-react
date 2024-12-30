from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.paginators import CustomPaginator
from api.permissions import UserOrAdminOrReadOnly
from api.serializers.user_serializers import (
    CustomUserSerializer,
    SubscribeSerializer,
)
from users.models import Subscribe, User


class CustomUserViewSet(UserViewSet):
    """Класс представления пользователей."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator
    permission_classes = (UserOrAdminOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    Subscribe.objects.filter(
                        author_id=OuterRef("id"), subscriber=user
                    )
                )
            )
        return queryset

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Создание и удаление подписки на автора."""
        subscriber = request.user
        if request.method == "POST":
            serializer = SubscribeSerializer(
                data={"subscriber": subscriber.id, "author": id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscribe, subscriber=subscriber, author__id=id
        ).delete()
        return Response(
            {"message": "Подписка удалена"}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок на авторов."""
        subscriber = request.user
        subscribe = (
            Subscribe.objects.filter(subscriber=subscriber)
            .prefetch_related("author__recipes")
            .annotate(recipes_count=Count("author__recipes"))
        ).order_by("author__email")
        page = self.paginate_queryset(subscribe)
        serializer = SubscribeSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
