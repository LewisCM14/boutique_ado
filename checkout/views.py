""" This module contains the views for the checkout app """

from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    """
    Renders the view for checking out.
    Collects the bag from the session,
    if bag is empty returns an error message.

    Creates an instance of the order form.
    Returns this as context to the view.
    Defines the template to be used.
    """
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51KddcYBD9ic51d7gNSHwKNN5iweUp64wzV0BcyP5VaM4Ff1ycCN9S7BButrBzmpi3v3GFjYugVEFnus1D13uQ0qG005RcQtcWe',  # noqa
        'client_secret_key': 'test client secret',
    }

    return render(request, template, context)
