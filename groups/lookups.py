from django.contrib.auth.models import User
from accounts.models import UserInstrument, Instrument
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


for instr in Instrument.objects.all():
    # register a separate LookupChannel for each instrument. Required for the form
    # where users are only invited who play the pre-selected instrument.
    @register("user_playing_"+instr.instrument)
    class UserLookupWithInstrument(UserLookup):
        model = User

        __name__ = str("UserLookupWith"+instr.instrument)

        def get_query(self, q, request):
            user_instrs = UserInstrument.objects.filter(instrument__instrument=instr.instrument)
            # print user_instrs
            users_playing = self.model.objects.filter(userinstrument__pk__in=user_instrs)
            # print users_playing
            return users_playing.filter(username__startswith=q)


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
