""" This module contains the image field widget for the product form """

from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _
# as _ is an alias for gettext_lazy, allows it to be called with '_'


class CustomClearableFileInput(ClearableFileInput):
    """
    inherits from built in class ClearableFileInput
    overrides the clear checkbox label
    the initial text the input text and the template name With custom values.
    has custom template folder with html file
    is called in forms.py for use
    """
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'  # noqa
