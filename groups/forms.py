from django import forms
from django.contrib.auth.models import User
from ajax_select.helpers import make_ajax_field
from accounts.models import UserInstrument, Instrument


class GroupSetupForm(forms.Form):
    """
    Form for starting up a new group - by sending out invitations to precisely
    one other user. (Subsequent invitations can then be made from the group's
    own page, even before the first invitee has accepted.)
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        options = UserInstrument.objects.filter(user=self.user)
        choices = [(instr.pk, instr.instrument) for instr in options.all()]
        super(GroupSetupForm, self).__init__(*args, **kwargs)
        self.fields["instrument"] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,
                                                      label="Instrument you will play")

    name = forms.CharField(max_length=100, label="Group name")
    invited_user = make_ajax_field(User, "username", "user_to_invite", label="Invite another user")
    desired_instruments=forms.ModelMultipleChoiceField(queryset=Instrument.objects.all(),
                                                       widget=forms.CheckboxSelectMultiple(),
                                                       label="Other desired instruments")
