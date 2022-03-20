""" This module containts the model for the order app """

import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField

from products.models import Product


class Order(models.Model):
    """
    when a user checks out.
    Use the information they put into the payment form
    to create an order instance.
    Then iterate through the items in the shopping bag.
    Creating an order line item for each one. Attaching it to the order.
    And updating the delivery cost, order total, and grand total.

    it's possible for the same customer to purchase the same things,
    twice on separate occasions. which would result in the code finding
    the first order in the database when they place
    the second one and thus the second-order never being added.
    We can combat this by adding two new fields to the order model.
    order_bag and stripe_pid
    The first is the original shopping bag that created it.
    And the other contains the stripe payment intent id
    which is guaranteed to be unique.
    """
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label="Country *", null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    # Calculated using model methods.
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0
    )
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=''
    )

    def _generate_order_number(self):
        """
        Prepended with an underscore by convention
        indicate it's a private method, Only to be used inside this class.

        Generate a random, unique 32 length order number using UUID
        """
        return uuid.uuid4().hex.upper()

    # pylint: disable=no-member
    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.

        Works by using the sum function across all the line-item total
        fields for all line items on this order.
        Adding a zero to the end of the line
        that aggregates all the line item totals.
        will prevent an error if all the line items
        from an order are manually deleted
        Making sure that this sets the order total to zero instead of none.
        Without this, the next line would cause an error
        because it would try to determine if
        none is less than or equal to the delivery threshold.
        The default behavior is to add a new field
        to the query set called line-item total sum.
        Which can then be set to the order total to that.
        When the order total calculated,
        then calculate the delivery cost using the free delivery threshold
        and the standard delivery percentage from settings file.
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0  # noqa
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100  # noqa
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    """
    order takes from the Order model.
    product takes from the Product model.
    Line item total is not editable.
    Automatically calculated when the line item is saved.
    """
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')  # noqa
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)  # noqa
    product_size = models.CharField(
        max_length=2, null=True, blank=True
    )  # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)  # noqa

    # pylint: disable=no-member
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    # pylint: disable=no-member
    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'
