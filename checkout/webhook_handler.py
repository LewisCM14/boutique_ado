""" This module handles stripes webhooks """

import json
import time

from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from products.models import Product
from profiles.models import UserProfile
from .models import Order, OrderLineItem


# pylint: disable=invalid-name
# pylint: disable=no-member
class StripeWH_Handler:
    """ Handles stripes webhooks """

    def __init__(self, request):
        """
        The init method of the class is a setup method
        that's called every time an instance of the class is created.
        It is used to assign the request as an attribute of the class
        Allowing access to any attributes of the request coming from stripe.
        """
        self.request = request

    def _send_confirmation_email(self, order):
        """
        Send the user a confirmation email
        starts with underscore as a private method, only used inside this class
        requires send_mail and render_to_string and settings file

        get the customers email from the order and store it in a variable.
        use the render_to_string method to render both email txt files.
        the first parameter being the file to render.
        the second being a context just like a template.
        This is how various context variables are sent to the email.
        to send the email use the send mail function.
        Giving it the subject the body the email to send from (SEE SETTINGS).
        And a list of emails sending to, i.e. the customer's email.
        it's just expecting to be passed an order to run. see webhook success
        handler for its call, this is where the order is passed.
        """
        customer_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [customer_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        Take the event stripe is sending us
        and return an HTTP response indicating it was received.
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe

        in case the form isn't submitted for some reason
        i.e. the user closes the page on the loading screen.
        collect the payment intent id, as well as the shopping bag
        and the users save info preference from the metadata
        added in the view and stripe JS file.
        also store the billing details, shipping details, and grand_total

        to ensure the data is in the form for the database.
        replace any empty strings in the shipping details with none.
        as stripe store them as blank strings
        which is not the same as the null value in the database.

        when a user checks out, everything should go well and the form
        will be submitted so the order should be in the database
        when this webhook is received.

        first check if the order exists already.
        try to get the order using all the information from the payment intent.
        using the iexact lookup field
        to make it an exact match but case-insensitive.
        If the order is found set order_exists to true,
        and return a 200 HTTP response to stripe,
        with the message that we verified the order already exists.

        if it doesn't create it here in the webhook.
        assume the order doesn't exist. with order_exists set to false.
        iterate through the bag items.
        the bag is loaded from the JSON version in the payment intent
        there is no form to save in this webhook to create the order
        it is created with order.objects.create
        using all the data from the payment intent, which is from the form.
        if anything goes wrong the order is deleted if it was created.
        And a 500 server error response is returned to stripe.
        This will cause stripe to automatically try the webhook again later.

        What if our view is just slow for some reason
        and hasn't created the order by the time the webhook from stripe does.
        in this instance the order will be created late.
        so the WH handler won't find the order when it first gets the webhook
        and will create the order itself resulting in the
        same order being added to the database twice, once the view finishes.
        This is a downfall of asynchronous applications
        i.e. when multiple processes are happening at once and some
        might depend on things we can't control.
        to handle this to some extent, a bit of delay is introduced.
        with the variable called attempt that is set to 1.
        using this a while loop is constructed that will execute 5 times.
        instead of creating the order if it's not found.
        it will increment attempt by 1
        And using pythons time module to sleep for one second.
        will cause the webhook handler to try to find the order five times
        over five seconds. if the order is found, break out of the loop.
        else create the order itself. returning a response to stripe detailing.
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            # only update info if save_info box was checked
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1  # noqa
                profile.default_street_address2 = shipping_details.address.line2  # noqa
                profile.default_county = shipping_details.address.state
                profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    # allows user to make 2 differant orders for the same items
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',  # noqa
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    # allows user to make 2 differant orders for the same items
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
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
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',  # noqa
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
