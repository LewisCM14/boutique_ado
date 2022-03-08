""" This module contains the admin logic for the products app """

from django.contrib import admin
from .models import Product, Category


admin.site.register(Product)
admin.site.register(Category)
