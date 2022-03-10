""" This module containts the views for the products app. """

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category


def all_products(request):
    """
    A view to show all products.
    Also shows sorting and search queries.

    Searching

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

    Filtering Via Category

    Start with it as none at the top of the view.
    And then check whether it exists in requests.get.
    If it does, split it into a list at the commas in the template url.
    Then use that list to filter the current query set of all products
    down to only products whose category name is in the list.

    filter all categories down to the ones whose name is in the list.
    converting the list of strings of category names passed through the URL
    into a list of actual category objects,
    so that we can access all their fields in the template.
    That list of category objects is called current_categories.
    return  to the context so we can use it in the template.

    Sorting Products
    Add both sort and direction equal to none at the top.
    in order to return the template properly when we're not using any sorting.

    Start by  checking whether sort is in request.get.
    In order to allow case-insensitive sorting on the name field,
    first annotate all the products with a new field.
    Check whether the sort key is equal to name.
    And if it is will set it to lower_name,
    which is the field created with the annotation.
    To do the annotation.
    products equals products.annotate lower_name equals lower name.
    Then use the lower function on the original name field.
    The reason for copying the sort parameter into the variable sortkey.
    Is to preserve the original field we want it to sort on name.
    But we have the actual field we're going to sort on,
    lower_name in the sort key variable.

    If it is then check whether the direction is there.
    check whether it's descending,
    If so add a minus in front of the sort key using string formatting.

    In order to actually sort the products use the order_by model method.

    Then return the current sorting methodology to the template.
    Since both the sort and the direction variables are stored
    this is done with with string formatting in current_sorting.

    Note that the value of this variable will be the string none_none.
    If there is no sorting.
    """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            # sets both equal to sort and sortkey
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")  # noqa
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)  # noqa
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
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
