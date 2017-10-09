from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    """
    We make just one tiny alteration to the Django default User Creation Form: we make the e-mail
    field required
    """
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
