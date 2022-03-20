""" This module contains the urls for the profile app """

from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile')
]
