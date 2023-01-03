from api.paginators import CustomPaginator
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscribe, User
from .serializers import CustomUserSerializer, SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    """ Класс представления пользователей. """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """ Создание и удаление подписки на автора. """
        subscriber = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, id=id)
        if subscriber == author:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if Subscribe.objects.filter(
                subscriber=subscriber, author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора!'}
                )
            subscribe = Subscribe.objects.create(
                subscriber=subscriber, author=author
            )
            serializer = SubscribeSerializer(
                subscribe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscribe, subscriber=subscriber, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """ Список подписок на авторов. """
        subscriber = request.user
        if subscriber.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        subscribe = Subscribe.objects.filter(subscriber=subscriber)
        page = self.paginate_queryset(subscribe)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
