""" This module handles stripes webhooks """

from django.http import HttpResponse


# pylint: disable=invalid-name
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

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        Take the event stripe is sending us
        and return an HTTP response indicating it was received.
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
