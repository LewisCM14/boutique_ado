""" This module contains the order form for the checkout app """

from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """
    The order form
    Inherits from the Order model.
    """
    class Meta:
        """
        Order form meta
        Fields does not render ant automatically calculated.
        """
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field

        First call the default init method
        to set the form up as it would be by default.
        """
        super().__init__(*args, **kwargs)
        # dict of placeholder for form fields
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        # Sets the autofocus attribute on the full name field to true.
        # Cursor will start in the full name field when page loads.
        self.fields['full_name'].widget.attrs['autofocus'] = True
        """
        Iterate through the forms fields adding a star to the placeholder
        if it's a required field on the model.
        Sets all the placeholder attributes to their values in the dict above.
        Adds a CSS class.
        Then removes the form fields labels.
        """
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False
