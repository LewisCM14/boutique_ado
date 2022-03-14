""" This module configures the checkout app """

from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    """ configuration settings for the checkout app."""
    name = 'checkout'

    def ready(self):
        """
        Import the signals module.
        Every time a line item is saved or deleted.
        update_total model method will be called.
        Updating the order totals automatically.
        """
        import checkout.signals
