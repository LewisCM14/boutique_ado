""" This module contains the urls for the products app. """

from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products')
]