""" This module contains the views for the bag app """

from django.shortcuts import render, redirect


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

    Create a variable called bag. Which accesses the requests session.
    Trying to get this variable if it already exists,
    and initializing it to an empty dictionary if it doesn't.

    Within the bag dict create a key of the items id,
    set it equal to the quantity.
    If the item is already in the bag, i.e.
    there's already a key in the bag dictionary matching the product id.
    Then increment its quantity accordingly.

    Then put the bag variable into the session.
    Which itself is just a python dictionary.
    """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})  # get or create

    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)
