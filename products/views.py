""" This module containts the views for the products app. """

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product


def all_products(request):
    """
    A view to show all products.
    Also shows sorting and search queries.

    q is the name of the text  input on the form.
    If the query is blank use Django messages framework,
    to attach an error message to the request.
    Then redirect back to the products url.

    Set's a variable equal to a Q object. Where the name contains the query.
    Or the description contains the query.
    The pipe here is what generates the or statement.
    And the i in front of contains makes the queries case insensitive.

    The filter method is then called on these queries and returned in
    the products variable.

    The query is added to the context as search term.
    set as none at the top of this view to ensure we don't get an error
    when loading the products page without a search term.
    """

    products = Product.objects.all()
    query = None

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
        if not query:
            messages.error(request, "You didn't enter any search criteria!")
            return redirect(reverse("products"))

        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    context = {
        'products': products,
        'search_term': query,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """
    A view to show individual product details.
    """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
