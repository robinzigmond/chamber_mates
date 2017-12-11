from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
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

    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["email"].required = True


class UserUpdateForm(forms.Form):
    """
    Form for a user to edit their email and password
    """
    email = forms.EmailField()
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput, required=False)

    # make sure we can pass the User instance in to the form
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)


    def clean_current_password(self):
        old = self.cleaned_data.get("current_password")
        if not old or check_password(old, self.user.password):
            return old
        else:
            raise forms.ValidationError("Please enter your correct current password")

    def clean_new_password2(self):
        first = self.cleaned_data.get("new_password1")
        second = self.cleaned_data.get("new_password2")
        if first != second:
            raise forms.ValidationError("The passwords must match!")
        return second


class ProfileForm(forms.ModelForm):
    """
    The form for a user to fill out their basic profile information (location,
    and maximum distance they are willing to travel)
    """
    
    # make the max_distance ForeignKey field have no "blank" option in the form:
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields["max_distance"].empty_label = None
        self.fields["max_distance"].widget.choices = self.fields["max_distance"].choices

    class Meta:
        model = Profile
        fields = ["description", "location", "max_distance"]
        widgets = {"description": forms.Textarea,
                   "location": GooglePointFieldWidget,
                   "max_distance": forms.RadioSelect}
        labels = {"description": "Tell other users a little about yourself",
                  "location": "Your location",
                  "max_distance": "Find players within this distance (miles)"}


class UserInstrumentForm(forms.ModelForm):
    """
    This form allows a user to select an instrument that they play, their rough
    standard on it - and what other instruments they are looking fo form a group with,
    and what standard they require the other players to be at.

    Copies of this form will be inserted into the profile form, with buttons the user
    can click to add or remove instruments
    """
    def __init__(self, *args, **kwargs):
        super(UserInstrumentForm, self).__init__(*args, **kwargs)
        fields = ["instrument", "standard", "desired_instruments", "accepted_standards"]
        for field in fields:
            self.fields[field].empty_label = None
            self.fields[field].widget.choices = self.fields[field].choices


    class Meta:
        model = UserInstrument
        fields = ["instrument", "standard", "desired_instruments", "accepted_standards"]
        widgets = {"instrument": forms.RadioSelect, "standard": forms.RadioSelect,
                   "desired_instruments": forms.CheckboxSelectMultiple,
                   "accepted_standards": forms.CheckboxSelectMultiple}
        labels = {"standard": "Please select your approximate standard on this instrument",
                  "desired_instruments": """What instruments do you want to form a group with?
                                          Select as many as you like.""",
                  "accepted_standards": """Which (approximate) standards do you want your partners to have?
                                           (select multiples if desired)"""}
