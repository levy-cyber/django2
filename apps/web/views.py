from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _


def home(request):
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    else:
        return render(request, "web/landing_page.html")


@user_passes_test(lambda u: u.is_superuser)
def simulate_error(request):
    raise Exception("This is a simulated error.")
