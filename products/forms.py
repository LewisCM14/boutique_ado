""" This module contains the product form used by store managers """

from django import forms
from .models import Product, Category


# pylint: disable=no-member
class ProductForm(forms.ModelForm):
    """
    Extends the model form
    """

    class Meta:
        """
        defines model used and fields required
        dunder or double underscore string
        called all which will include all the fields.
        """
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        override the init method to make changes to the fields.
        categories to show up in the form using their friendly name.
        first get all the categories.
        create a list of tuples of the friendly names associated with the ids.
        use the friendly names, to update the category field on the form.
        To use those for choices instead of using the id.
        The effect of this will be seen in the select box
        that gets generated in the form.
        Instead of seeing the category ID or the name field
        will see the friendly name.
        then iterate through the rest of these fields
        and set some classes on them to make them match
        the theme of the store.
        """
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
