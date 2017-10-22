from django.contrib.auth.models import User
from .models import Message

def messages(request):
    """
    Context processor to fetch all unread messages that the user has
    """
    if isinstance(request.user, User):
        user_messages = Message.objects.filter(user_to=request.user, seen=False)
        return({"user_messages": user_messages})

    # make sure no error is returned if the user isn't logged in:
    return ({"user_messages": None})
