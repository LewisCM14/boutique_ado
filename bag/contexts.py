""" This module contants a context processor for the shopping bag """

from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.conf import settings
from products.models import Product


def bag_contents(request):
    """
    returns the context processor for the shopping bag,
    making the dict available for all templates across the application.

    Free delivery if they spend more than the amount specified
    in the free delivery threshold in settings.py.
    Check whether it's less than that threshold.
    If it is less calculate delivery as the total
    multiplied by the standard delivery percentage
    from settings.py. which in this case is 10%.

    I'm using the decimal function since this is a financial transaction
    and using float is susceptible to rounding errors.

    If the total is greater than or equal to the threshold
    set delivery and the free_delivery_delta to zero.

    calculate the grand total. add the delivery charge to the total.

    In order to populate bag_items, total and product_count.
    Create a variable called bag. Which accesses the requests session.
    Trying to get this variable if it already exists,
    and initializing it to an empty dictionary if it doesn't.

    In the case of an item with no sizes.
    The item data will just be the quantity.
    But in the case of an item that has sizes the
    item data will be a dictionary of all the items by size.

    If the item has no sizes.
    Evident by checking whether or not the item data is an integer.
    If it's an integer the item data is just the quantity.

    Iterate through all the items in the shopping bag.
    And along the way, tally up the total cost and product count.
    Add the products and their data to the bag items list.

    If it's a dictionary need to iterate through
    the inner dictionary of items_by_size
    incrementing the product count and total accordingly.
    For each of these items, add the size to the bag items
    returned to the template as well.

    Add a dictionary to the list of bag items containing the id & quantity,
    But also the product object itself.
    Allowing access to all the other fields,
    when iterating through the bag items in our templates.
    """

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():  # bag from session
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)  # get product
            total += item_data * product.price  # add quantity x price to total
            product_count += item_data  # increment product count by quantity
            bag_items.append({  # add list of bag items
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            product = get_object_or_404(Product, pk=item_id)
            # item_data as a dict
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,  # quantity from inner dict
                    'product': product,
                    'size': size,
                })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
