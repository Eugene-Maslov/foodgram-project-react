from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=16,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    color = models.CharField(max_length=16, verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name
