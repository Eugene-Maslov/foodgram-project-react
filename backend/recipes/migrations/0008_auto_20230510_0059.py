# Generated by Django 3.2 on 2023-05-10 00:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_rename_tag_recipe_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-id',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ['-id'], 'verbose_name': 'Рецепт - ингредиент', 'verbose_name_plural': 'Рецепты - ингредиенты'},
        ),
    ]
