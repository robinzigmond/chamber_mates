from django.contrib.auth.models import User
from accounts.models import UserInstrument
from ajax_select import register, LookupChannel

@register("user_to_invite")
class UserLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(username__startswith=q)

    def format_match(self, user):
        return "<span class='autocomplete-option'>%s</span>" % user.username

    def check_auth(self, request):
        if request.user.is_authenticated() :
            return True


@register("instrument")
class InstrumentLookup(LookupChannel):
    model = UserInstrument

    def get_query(self, q, request):
        return self.model.objects.filter(user__username=q)

    def get_result(self, obj):
        return obj.instrument.instrument

    def check_auth(self, request):
        if request.user.is_authenticated():
            return True
