""" This module contains the views for the profiles app """

from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm


# pylint: disable=redefined-outer-name
def profile(request):
    """
    Display the user's profile.
    Populate it with the user's current profile information.
    And return it to the template
    use the profile and the related name on the order model.
    To get the users orders and return those to the template

    the post handler for the profile view:
    if the request method is post.
    Create a new instance of the user profile form,
    using the post data.
    And tell it the instance we're updating
    is the profile we've just retrieved above.
    Then if the form is valid. save it and add a success message.
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)
