import os.path

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.settings import MEDIA_ROOT
from foodstuffs_assistant.models import Ingredient, Tag
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, PostRecipeSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer)


class CustomViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(CustomViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(CustomViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination
    search_fields = ('name',)

    def get_queryset(self):
        user = self.request.user
        if self.request.query_params.get('is_favorited'):
            return Recipe.objects.filter(favorites__user=user)
        if self.request.query_params.get('is_in_shopping_cart'):
            return Recipe.objects.filter(added_to_cart__user=user)
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return PostRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        image_path = os.path.join(MEDIA_ROOT, str(instance.image))
        os.remove(image_path)
        instance.delete()

    @action(
        url_path='download_shopping_cart',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = list(shopping_cart.values_list('recipe_id', flat=True))
        shopping_list = RecipeIngredient.objects.filter(
            recipe__in=recipes).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount'))
        shopping_list_text = 'Список покупок:\n\n'
        for item in shopping_list:
            shopping_list_text += (
                f"{item['ingredient__name']}: {item['total_amount']} "
                f"{item['ingredient__measurement_unit']}\n")
        filename = f'{request.user.username}_shopping_cart.txt'
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def common_method(self, request, pk, table):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if not table.objects.filter(user=user, recipe=recipe).exists():
                table(user=user, recipe=recipe).save()
                serializer = RecipeShortSerializer
                return Response(serializer(recipe).data,
                                status=status.HTTP_201_CREATED)
            return Response('Этот рецепт уже добавлен!',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            table.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        url_path='shopping_cart',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        return RecipeViewSet.common_method(self, request, pk, ShoppingCart)

    @action(
        url_path='favorite',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        return RecipeViewSet.common_method(self, request, pk, Favorite)
