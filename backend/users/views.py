from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminOrReadOnly
from api.serializers import GetUserSerializer, UserSubscriptionSerializer
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    @action(
        url_path='subscriptions',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        limit = self.request.query_params.get('recipes_limit')
        my_subs = User.objects.filter(
            following__user=request.user).order_by('id')
        pages = self.paginate_queryset(my_subs)
        serializer = UserSubscriptionSerializer(pages, many=True)
        if limit:
            for user in serializer.data:
                if user.get('recipes'):
                    user['recipes'] = user.get('recipes')[:int(limit)]
        return self.get_paginated_response(serializer.data)

    @action(
        url_path='subscribe',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if not Follow.objects.filter(user=user, author=author).exists():
                if user != author:
                    Follow(user=user, author=author).save()
                    serializer = UserSubscriptionSerializer
                    return Response(serializer(author).data,
                                    status=status.HTTP_201_CREATED)
                return Response('Нельзя подписаться на самого себя!',
                                status=status.HTTP_400_BAD_REQUEST)
            return Response('Вы уже подписаны!',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
