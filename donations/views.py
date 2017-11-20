# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from .forms import DonationForm

stripe.api_key = settings.STRIPE_SECRET

# Create your views here.
@login_required(login_url=reverse_lazy("login"))
def donate(request):
    """
    view to handle the donations form
    """
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            try:
                customer = stripe.Charge.create(
                    amount=int(form.cleaned_data["amount"]*100), # convert to cents for Stripe processing
                    currency="USD",
                    description=request.user.username,
                    card=form.cleaned_data["stripe_id"],
                )
                if customer.paid:
                    messages.success(request, "Thank you very much for your donation!")
                    return redirect(reverse("dashboard"))
                else:
                    messages.error(request, """Something went wrong with your payment!
                                               Please check your card details and try again.""")
            except stripe.error.CardError:
                messages.error(request, "Sorry, your card was declined.")
    else:
        form = DonationForm(initial={"amount":5})

    args = {"active": "donate", "form": form, "publishable": settings.STRIPE_PUBLISHABLE}
    args.update(csrf(request))

    return render(request, "donations/donate.html", args)
