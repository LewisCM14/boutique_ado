""" This module contants a context processor for the shopping bag """

from decimal import Decimal
from django.conf import settings


def bag_contents(_request):
    """
    returns the context processor for the shopping bag,
    making the dict available for all templates across the application.

    free delivery if they spend more than the amount specified
    in the free delivery threshold in settings.py.
    check whether it's less than that threshold.
    If it is less calculate delivery as the total
    multiplied by the standard delivery percentage
    from settings.py. which in this case is 10%.

    I'm using the decimal function since this is a financial transaction
    and using float is susceptible to rounding errors.

    If the total is greater than or equal to the threshold
    set delivery and the free_delivery_delta to zero.

    calculate the grand total. add the delivery charge to the total.
    """

    bag_items = []
    total = 0
    product_count = 0

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
