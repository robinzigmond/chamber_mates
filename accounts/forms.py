from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.gis import forms
from mapwidgets.widgets import GooglePointFieldWidget
from .models import Profile, UserInstrument

class UserRegistrationForm(UserCreationForm):
    """
    We make just one tiny alteration to the Django default User Creation Form: we make the e-mail
    field required
    """
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    """
    The form for a user to fill out their basic profile information (location,
    and maximum distance they are willing to travel)
    """
    
    # make the max_distance ForeignKey field have no "blank" option in the form:
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.base_fields["max_distance"].empty_label = None
        self.fields["max_distance"].widget.choices = self.fields["max_distance"].choices

    class Meta:
        model = Profile
        fields = ["location", "max_distance"]
        widgets = {"location": GooglePointFieldWidget,
                   "max_distance": forms.RadioSelect}
