from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodstuffs_assistant.models import Ingredient, Tag
from recipes.models import Recipe, RecipeIngredient
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from users.models import User

from .fields import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSeriaizer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class PostRecipeIngredientSeriaizer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class GetUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and user.follower.filter(author=obj.id).exists())


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')
        model = User


class RecipeSerializer(serializers.ModelSerializer):
    ingredient = RecipeIngredientSeriaizer(
        many=True,
        read_only=True,
        source='recipeingredients')
    tags = TagSerializer(many=True, read_only=True)
    author = GetUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredient', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and user.favorites.filter(recipe=obj.id).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and user.added_to_cart.filter(recipe=obj.id).exists())


class PostRecipeSerializer(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = PostRecipeIngredientSeriaizer(many=True)
    image = Base64ImageField()
    author = GetUserSerializer(read_only=True)

    class Meta:
        fields = ('id', 'author', 'name', 'tags', 'text', 'image',
                  'ingredients', 'cooking_time')
        model = Recipe

    def new_ingredients(self, curr_ingredients, curr_recipe):
        ingredient_objs = [
            RecipeIngredient(
                recipe=curr_recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=new_ingredient.get('id')),
                amount=new_ingredient.get('amount')
            )
            for new_ingredient in curr_ingredients
        ]
        # output = RecipeIngredient.objects.bulk_create(ingredient_objs)
        RecipeIngredient.objects.bulk_create(ingredient_objs)

    def create(self, validated_data):
        post_ingredients = validated_data.pop('ingredients')
        post_tags = validated_data.pop('tags')
        new_recipe = Recipe.objects.create(**validated_data)
        new_recipe.tags.set(post_tags)
        self.new_ingredients(post_ingredients, new_recipe)
        return new_recipe

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def update(self, instance, validated_data):
        update_ingredients = validated_data.pop('ingredients')
        update_tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.set(update_tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.new_ingredients(update_ingredients, instance)
        return instance

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError('Нужно добавить хотя бы один ингредиент!')
        ingred_list = [[item['id'], item['amount']] for item in ingredients]
        for ingredient in ingred_list:
            if ingred_list.count(ingredient[0]) > 1:
                raise ValidationError('Ингредиенты не могут повторяться!')
            if int(ingredient[1]) <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0!')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('Нужно добавить хотя бы один тэг!')
        return tags


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class UserSubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeShortSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def get_is_subscribed(self, object):
        return True

    def get_recipes_count(self, object):
        return Recipe.objects.filter(author=object).count()
