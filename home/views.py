""" This module contains the views for the home app """

from django.shortcuts import render


def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')
