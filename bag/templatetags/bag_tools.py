""" This module containts a function used to calculate the bag subtotal """

from django import template

register = template.Library()


@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    """
    Returns the correct subtotal price for the bag.

    Create a variable called register.
    Which is an instance of template.library
    And then use the register filter decorator
    to register our function as a template filter.
    """
    return price * quantity
