from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodstuffs_assistant.models import Ingredient, Tag
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart

from .filters import RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, PostRecipeSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = CustomPageNumberPagination
    search_fields = ('name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = CustomPageNumberPagination
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return PostRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        url_path='download_shopping_cart',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        shopping_list = RecipeIngredient.objects.filter(recipe__in=recipes
            ).values('ingredient').annotate(amount=Sum('amount'))
        shopping_list_text = 'Список покупок:\n\n'
        for item in shopping_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            shopping_list_text += (
                f'{ingredient.name}: {amount} '
                f'{ingredient.measurement_unit}\n')
        filename = f'{request.user.username}_shopping_cart.txt'
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(
        url_path='shopping_cart',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if not ShoppingCart.objects.filter(user=user,
                                               recipe=recipe).exists():
                obj = ShoppingCart(user=user, recipe=recipe).save()
                serializer = RecipeShortSerializer
                return Response(serializer(recipe).data,
                                status=status.HTTP_201_CREATED)
            return Response('Этот рецепт уже добавлен!',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        url_path='favorite',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                obj = Favorite(user=user, recipe=recipe).save()
                serializer = RecipeShortSerializer
                return Response(serializer(recipe).data,
                                status=status.HTTP_201_CREATED)
            return Response('Этот рецепт уже добавлен!',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
