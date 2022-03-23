""" This module containts the views for the products app. """

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from .forms import ProductForm


# pylint: disable=no-member
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
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

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
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """
    Add a product to the store
    if the request method is post.
    instantiate a new instance of the product form from request.post
    and include request .files also In order to capture in the image.
    Then check if form.is_valid. And if so save it.
    Add a simple success message. And redirect to the same view.
    If there are any errors on the form.
    attach a error message telling the user to check their form
    the empty form instantiation is in the 'if request' else block
    so it doesn't wipe out the form errors.
    """
    # Allows only superusers access to this views functionality
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            # redirect to the products detail page
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')  # noqa
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """
    Edit a product in the store
    take the request and the product ID the user is going to edit.
    pre-fill the form by getting the product using get_object_or_404
    And then instantiating a product form using the product.
    tell it which template to use.
    Give it a context so the form and the product will be in the template.
    And then return the render statement.

    if the request method is post.
    instantiate a form using request.post and request.files
    tell it the specific instance to update is the product obtained above.
    If the form is valid save it Add a success message
    And then redirect to the product detail page using the product id.
    Otherwise, add an error message and return the form
    which will have the errors attached.
    """
    # Allows only superusers access to this views functionality
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')  # noqa
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """
    Delete a product from the store
    take the request and the product id to be deleted.
    start by getting the product With get_object_or_404
    And then call product.delete.
    Add a success message.
    And redirect back to the products page.
    """
    # Allows only superusers access to this views functionality
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
