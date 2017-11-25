from django.contrib.auth.models import User
from ajax_select import register, LookupChannel
from accounts.models import UserInstrument, Instrument

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


# register a separate LookupChannel for each instrument. Required for the form
# where users are only invited who play the pre-selected instrument.
# I eventually found the right way to do this thanks to zondo's reply on the
# following StackOverflow thread:
# https://stackoverflow.com/questions/36159455/create-multiple-classes-from-list-of-strings
instrument_lookups = {}
for instr in Instrument.objects.all():
    # need to do the (manual) Python equivalent of a Javascript IIFE, to make sure that
    # the get_query method uses the correct value of instr each time through the loop.
    # (Otherwise all classes end up using whatever the last value in the loop is.)
    def make_lookup_class(instr_obj):
        @register("user_playing_"+instr_obj.instrument)
        class UserLookupWithInstrument(UserLookup):
            model = User

            def get_query(self, q, request):
                user_instrs = UserInstrument.objects.filter(instrument__instrument=instr_obj.instrument)
                users_playing = self.model.objects.filter(userinstrument__pk__in=user_instrs)
                return users_playing.filter(username__startswith=q)
        
        name = "UserLookupWith"+instr_obj.instrument
        UserLookupWithInstrument.__name__ = str(name)
        instrument_lookups[name] = UserLookupWithInstrument

    make_lookup_class(instr)


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
