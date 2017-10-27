from django.contrib.gis import forms
from .models import Message


class MessageForm(forms.ModelForm):
    """
    The form a user fills in when creating a new message
    """
    class Meta:
        model = Message
        fields = ["user_to", "title", "message"]
