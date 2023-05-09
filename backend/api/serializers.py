import base64

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodstuffs_assistant.models import Ingredient, Tag
from recipes.models import Recipe, RecipeIngredient
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


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
        if (not user.is_anonymous
            and user.follower.filter(author=obj.id).exists()):
            return True
        return False


class UserSerializer(UserCreateSerializer):

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
        if (not user.is_anonymous
            and user.favorites.filter(recipe=obj.id).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if (not user.is_anonymous
            and user.added_to_cart.filter(recipe=obj.id).exists()):
            return True
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
        for new_ingredient in curr_ingredients:
            RecipeIngredient.objects.create(
                recipe = curr_recipe,
                ingredient = get_object_or_404(
                    Ingredient, id=new_ingredient.get('id')),
                amount = new_ingredient.get('amount'))

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
        ingredients_list = [item['id'] for item in ingredients]
        for ingredient in ingredients_list:
            if ingredients_list.count(ingredient) > 1:
                raise ValidationError('Ингредиенты не могут повторяться!')
            if int(ingredient['amount']) <= 0:
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
