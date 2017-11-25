from django.contrib.auth.models import User
from .models import Invitation

def new_invites(request):
    """
    Context processor to fetch all new group invitations for the user
    """
    if isinstance(request.user, User):
        invites = Invitation.objects.filter(invited_user=request.user)
        return({"new_invites": invites})

    # make sure no error is returned if the user isn't logged in:
    return ({"new_invites": None})
