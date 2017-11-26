from django import forms
from django.contrib.auth.models import User
from ajax_select.helpers import make_ajax_field
from ajax_select.fields import AutoCompleteField
from accounts.models import UserInstrument, Instrument
from .models import Invitation


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
    invited_user = make_ajax_field(User, "username", "user_to_invite",
                                   label="Invite another user",
                                   help_text="")
    desired_instruments=forms.ModelMultipleChoiceField(queryset=Instrument.objects.all(),
                                                       widget=forms.CheckboxSelectMultiple(),
                                                       label="Other desired instruments",
                                                       required=False)

class InvitationForm(forms.ModelForm):
    """
    A form for sending an invitation to a user to join an already-existing group
    """
    def __init__(self, *args, **kwargs):
        instr = kwargs.pop("instr", None)
        super(InvitationForm, self).__init__(*args, **kwargs)
        self.fields["group"].empty_label = None
        self.fields["group"].widget.choices = self.fields["group"].choices
        self.fields["invited_instrument"].empty_label = None
        self.fields["invited_instrument"].widget.choices = self.fields["invited_instrument"].choices
        self.fields["invited_user"] = AutoCompleteField("user_playing_"+instr,
                                                        label="User to invite",
                                                        help_text=None)

    class Meta:
        model = Invitation
        fields = ["group", "invited_instrument"]
        widgets = {"invited_instrument": forms.RadioSelect}


    def clean_invited_user(self):
        try:
            data = self.cleaned_data["invited_user"]
            return User.objects.get(username=data)
        except User.DoesNotExist:
            raise forms.ValidationError("Please enter an existing username")


class DecideOnInvitation(forms.Form):
    """
    A "mini-form" for the user to accept or decline an invitation to join a group.
    """
    CHOICES = (("accept", "accept"), ("decline", "decline"))
    accept_or_decline = forms.ChoiceField(label="", widget=forms.RadioSelect,
                                          choices=CHOICES)
