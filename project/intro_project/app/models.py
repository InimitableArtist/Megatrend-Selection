from django.db import models

__all__ = ['Item', 'Category']

class Category(models.Model):
    name = models.CharField(max_length = 150, unique = True)
    uuid = models.CharField(max_length = 36, unique = True)

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    name = models.CharField(max_length = 150)
    uuid = models.CharField(max_length = 36, unique = True)

    category = models.ForeignKey(Category)

    def __str__(self) -> str:
        return self.name