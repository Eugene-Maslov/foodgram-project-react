from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminOrReadOnly
from api.serializers import GetUserSerializer, UserSubscriptionSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer
    filter_backends = (filters.SearchFilter,)
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('username',)

    @action(
        url_path='subscriptions',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        # my_subs = User.objects.filter(following__user=request.user)
        # my_subs = User.objects.filter(author__user=self.request.user)
        my_subs = User.objects.filter(author__user=request.user)
        return Response(UserSubscriptionSerializer(my_subs, many=True).data,
                        status=status.HTTP_200_OK)

    @action(
        url_path='subscribe',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if not Follow.objects.filter(user=user, author=author).exists():
                if user != author:
                    # obj = Follow(user=user, author=author).save()
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
