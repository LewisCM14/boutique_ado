""" This module contains the admin logic for the products app """

from django.contrib import admin
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    The admin class for the Products model.
    extends from the base.
    """
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image'
    )

    ordering = ('sku',)


@admin.register(Category)
class CatergoryAdmin(admin.ModelAdmin):
    """
    The admin class for the Products model.
    extends from the base.
    """
    list_display = (
        'friendly_name',
        'name',
    )
