""" This module contains the admin logic for the checkout app """

from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """
    Inline item allow add and edit line items in the admin,
    from inside the order model.
    Will see a list of editable line items on the same page.

    To add it to the order admin interface.
    Add the inlines option in the order admin class.

    This admin is registered in the order admin.
    """
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    The admin class for the order model.

    Read only fields calculated by model methods.
    Fields is specified to ensure the order
    stays the same as it appears in the model.

    Ordered by date in reverse chronological order
    """
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag',
                       'stripe_pid',)

    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag',
              'stripe_pid')

    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    ordering = ('-date',)
