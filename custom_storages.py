""" This module is for AWS and Django settings using Boto """

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    custom class called static storage.
    inherits from django storages. Giving it all its functionality.
    tells django we want to store static files
    in a location from the settings.
    """
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    """
    custom class called media storage.
    inherits from django storages. Giving it all its functionality.
    tells django we want to store media files
    in a location from the settings.
    """
    location = settings.MEDIAFILES_LOCATION


# pylint: disable=pointless-string-statement
"""
when our project is deployed to Heroku.
Heroku will run python3 manage.py collectstatic during the build process.
Which will search through all apps and project folders
looking for static files.
And it will use the s3 custom domain in settings.py
in conjunction with the custom storage classes
that tell it the location at that URL.
Where we'd like to save things.
So in effect when the USE_AWS setting is true.
Whenever collectstatic is run.
Static files will be collected into a static folder in our s3 bucket.
"""
