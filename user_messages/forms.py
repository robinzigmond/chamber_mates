from django.contrib.gis import forms
from django.contrib.auth.models import User
from ajax_select.fields import AutoCompleteField
from .models import Message


class MessageForm(forms.ModelForm):
    """
    The form a user fills in when creating a new message
    """
    user_to = AutoCompleteField("usernames", required=False, help_text=None,
                                label="To")

    class Meta:
        model = Message
        fields = ["title", "message"]


    def clean_user_to(self):
        try:
            data = self.cleaned_data["user_to"]
            return User.objects.get(username=data)
        except User.DoesNotExist:
            raise forms.ValidationError("Please enter an existing username")
