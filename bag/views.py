""" This module contains the views for the bag app """

from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages

from products.models import Product


def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """
    Add a quantity to the specified product to the shopping bag.
    Get the quantity from the form with request.post.get quantity.
    convert it to an integer as it comes from the template as a string.
    Get the redirect URL from the form,
    redirect to once the process here is finished.

    Set size to none, check if product has size field and update accordingly.

    Create a variable called bag. Which accesses the requests session.
    Trying to get this variable if it already exists,
    and initializing it to an empty dictionary if it doesn't.

    If the item has a size field
    add as dictionary with a key of items_by_size to bag.

    As may have multiple items with this item id. But different sizes.
    This allows us to structure the bags such that
    Can have a single item id for each item. But still track multiple sizes.

    If the item is already in the bag.
    Check if another item of the same id and same size already exists.
    If so increment the quantity for that size,
    otherwise just set it equal to the quantity.

    Then put the bag variable into the session.
    Which itself is just a python dictionary.
    """
    product = Product.objects.get(pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})  # get or create

    if size:
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity
            messages.error(request, f'Added {product.name} to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """
    Adjust the quantity of the specified product to the specified amount.

    If quantity is greater than zero set the items quantity
    accordingly otherwise just remove the item.

    If there's a size, drill into the
    items by size dictionary, find that specific size and either set its
    quantity to the updated one or remove it if the quantity submitted is zero.
    """

    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})  # get or create

    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:  # Items by size dict false
                bag.pop(item_id)
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id)

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """
    Removes items from the shopping bag.

    If size is in request.post.
    Delete that size key in the items by size dictionary.

    If that's the only size in the bag.
    i.e. if the items by size dictionary is now empty,
    which will evaluate to false.
    Remove the entire item id so theres not an empty items
    by size dictionary hanging around.

    If there is no size. 'pop' item out of the bag.

    View will be posted to from a JavaScript function.
    Return an actual 200 HTTP response.
    Implying that the item was successfully removed.
    """
    try:
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})  # get or create

        if size:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            bag.pop(item_id)

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(status=500)
