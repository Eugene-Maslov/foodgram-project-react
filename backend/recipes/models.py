from django.core.validators import MinValueValidator
from django.db import models

from foodstuffs_assistant.models import Ingredient, Tag
from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор')
    name = models.CharField(max_length=256, blank=False,
                            verbose_name='Название блюда')
    image = models.ImageField(upload_to='recipes/images/', null=True,
                              blank=False, default=None,
                              verbose_name='Фотография блюда',
                              help_text='Загрузите картинку')
    text = models.TextField(null=True, blank=False, verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient, blank=False,
                                         through='RecipeIngredient',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, blank=False,
                                  related_name='recipes',
                                  verbose_name='Тэг')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name='Время готовки')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipeingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Рецепт - ингредиент'
        verbose_name_plural = 'Рецепты - ингредиенты'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',)
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Рецепт')

    class Meta:
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_favorites',)
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='added_to_cart', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='added_to_cart', verbose_name='Рецепт')

    class Meta:
        verbose_name_plural = 'Продуктовая корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_cart',)
        ]
