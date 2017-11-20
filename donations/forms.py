from django import forms
from django.utils import timezone

class DonationForm(forms.Form):
    MONTH_ABBREVIATIONS = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    MONTH_CHOICES = list(enumerate(MONTH_ABBREVIATIONS, 1))
    current_year = timezone.now().year
    YEAR_CHOICES = [(i, i) for i in range(current_year, current_year+21)]
 
    credit_card_number = forms.CharField(label="Credit card number")
    cvv = forms.CharField(label="Security code (CVV)")
    expiry_month = forms.ChoiceField(label="Month", choices=MONTH_CHOICES)
    expiry_year = forms.ChoiceField(label="Year", choices=YEAR_CHOICES)
    stripe_id = forms.CharField(widget=forms.HiddenInput)
    amount = forms.FloatField(min_value=0, widget=forms.NumberInput(attrs={"step": "0.01"}),
                              label="Amount (US$)")
