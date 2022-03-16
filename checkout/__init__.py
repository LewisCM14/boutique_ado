"""
Tell django the name of the default config class for the app
which is checkout.apps.CheckoutConfig.
this class is from apps.py where the signals module is imported.
Without this line in the init file, django wouldn't know about the
custom ready method so signals wouldn't work.
"""

default_app_config = 'checkout.apps.CheckoutConfig'
