""" This module contains signals used in the order app """

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem

# The receiver decorator, receives post saved signals.
# From the OrderLineItem model.
# See apps.py for how these signals are implimented.


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create

    This function which will handle signals from the post_save event.
    The parameters refer to the:
    sender of the signal. In this case OrderLineItem.
    The actual instance of the model that sent it.
    A boolean sent by django referring to whether
    this is a new instance or one being updated.
    Then any keyword arguments.

    Access instance.order which refers to the order
    this specific line item is related to.
    Then call the update_total method on it.
    """
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()
