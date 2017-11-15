from django.contrib.auth.models import User
from .models import Match

def unknown_matches(request):
    """
    Context processor to fetch all new matches for the user
    """
    if isinstance(request.user, User):
        new_matches = Match.objects.filter(requesting_user=request.user, known=False)
        return({"new_matches": new_matches})

    # make sure no error is returned if the user isn't logged in:
    return ({"new_matches": None})
