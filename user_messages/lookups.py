from django.contrib.auth.models import User
from ajax_select import register, LookupChannel

@register("usernames")
class UsernameLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(username__startswith=q)

    def format_match(self, user):
        return "<span class='autocomplete-option'>%s</span>" % user.username

    def check_auth(self, request):
        if request.user.is_authenticated() :
            return True
