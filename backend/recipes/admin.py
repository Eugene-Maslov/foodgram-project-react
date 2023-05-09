from django.contrib import admin

from .models import Favorite, Recipe, RecipeIngredient, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('count_favorite',)
    inlines = (RecipeIngredientInline,)
    add_fieldsets = (
        (None, {'fields': ('count_favorite',),}),
    )

    def count_favorite(self, obj):
        return obj.favorites.count()
    count_favorite.short_description = 'Количество добавлений в избранное'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')

admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
