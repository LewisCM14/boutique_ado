""" This module contains the views for the profiles app """

from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from checkout.models import Order

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


def order_history(request, order_number):
    """
    get the order
    add a message letting the user know
    they're looking at a past order confirmation.
    give it a template and some context which will include the order number.
    using the checkout success template
    as that template already has the layout for rendering a order confirmation.
    """
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
