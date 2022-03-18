""" This module contains the stripe webhooks """

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import stripe

from checkout.webhook_handler import StripeWH_Handler


@require_POST  # prevents a GET request
@csrf_exempt  # stripe doesn't send csrf token
def webhook(request):
    """
    Listen for webhooks from Stripe

    Modifying the webhook view to use the webhook handler:
    Create an instance of it passing in the request.
    Then create a dictionary called event map
    the dictionaries keys will be the names of the webhooks coming from stripe.
    While its values will be the actual methods inside the handler.
    Get the type of the event from stripe
    which will be stored in a key called type.
    This will return something like payment intent.succeeded
    or payment intent.payment failed.
    Then look up the key in the dictionary.
    And assign its value to a variable called event handler
    At this point, event handler is nothing more than an alias
    for whatever function we pulled out of the dictionary.
    Can be called like any other function.
    So to get the response from the webhook handler
    we can just call event handler, and pass it the event.
    Finally, return the response to stripe.
    """
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,  # noqa
    }

    # Get the webhook type from Stripe
    event_type = event['type']

    # If there's a handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)
    return response
