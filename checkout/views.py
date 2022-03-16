""" This module contains the views for the checkout app """

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

import stripe

from bag.contexts import bag_contents
from products.models import Product
from .forms import OrderForm
from .models import Order, OrderLineItem


def checkout(request):
    """
    Renders the view for checking out.
    Collects the bag from the session,
    if bag is empty returns an error message.

    Creates an instance of the order form.
    Returns this as context to the view.
    Defines the template to be used.

    on POST request, creates an instance of the bag & order form in form_data
    checks form is valid, if so saves. Then iterates through the bag items
    and creates a line item (see order model in checkout view).
    First get the Product ID out of the bag.
    Then if its value is an integer the item that doesn't have sizes.
    So the quantity will just be the item data.
    If the item has sizes. iterate through each size and create a line item
    in case a product isn't found add an error message.
    Delete the empty order and return the user to the shopping bag page.

    If the user wants to save their profile information to the session.
    redirect them to checkout_success.html template.
    order number is passed as an argument to this template. (saved line 73)

    If the order form isn't valid, attach a message detailing
    and redirect back to the checkout page at the bottom of this view
    with the form errors shown.

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

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():  # noqa
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "  # noqa
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))  # noqa
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")  # noqa
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    First check whether the user wanted to save their information
    by getting that from the session in 'save_info'

    collects order number created in checkout view above,
    returns this to template

    Then attach a success message
    letting the user know what their order number is.
    And that a confirmation email will be sent to the email in the form.
    Finally delete the user shopping bag from the session
    Set the template and the context. And render the template.
    """
    # save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
