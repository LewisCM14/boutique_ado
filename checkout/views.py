""" This module contains the views for the checkout app """

from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

import stripe

from bag.contexts import bag_contents
from .forms import OrderForm


def checkout(request):
    """
    Renders the view for checking out.
    Collects the bag from the session,
    if bag is empty returns an error message.

    Creates an instance of the order form.
    Returns this as context to the view.
    Defines the template to be used.

    Collects the bag total for use with strip:
    Uses context processor in the bag app. In checkouts.view.py.
    This function returns a Python dictionary.
    Pass it the request and get the same dictionary here in the view.
    Store that in a variable called current bag.
    So not to overwrite the bag variable that already exists.
    To get the total, collect the grand_total key out of the current bag.

    Then multiply that by a hundred.
    Then round it to zero decimal places using the round function.
    Stripe requires the amount to charge as an integer.
    uses the stripe keys from settings.py to setup the payment.
    Stores this payment in the intent object.
    This object can then have it's dict keys referenced. (see client_secret)
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    current_bag = bag_contents(request)
    total = current_bag['grand_total']

    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret_key': intent.client_secret,
    }

    return render(request, template, context)
