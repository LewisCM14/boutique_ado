""" Contains the model for the profile app """

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


# pylint: disable=no-member
class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history

    specifies that each user can only have one profile.
    And each profile can only be attached to one user.

    The other fields in this model are
    the delivery information fields the
    user is able to provide defaults for.
    These come directly from the order model.
    all these fields are optional.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)  # noqa
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)  # noqa
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)  # noqa
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)  # noqa
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country', null=True, blank=True)  # noqa

    def __str__(self):
        return self.user.username


# pylint: disable=no-member
# pylint: disable=unused-argument
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    receiver for the post save event from the user model.
    So that each time a user object is saved.
    automatically either create a profile for them
    if the user has just been created.
    Or just save the profile to update it if the user already existed.
    import post save and receiver in order model for the signal to work.
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
