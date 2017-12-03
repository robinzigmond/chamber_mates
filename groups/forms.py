from django import forms
from django.contrib.auth.models import User
from ajax_select.helpers import make_ajax_field
from ajax_select.fields import AutoCompleteField
from accounts.models import UserInstrument, Instrument
from .models import Invitation, GroupMessage


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


class GroupUpdateForm(forms.Form):
    """
    Form to update the name and/or desired instruments of a group. Doesn't work well as a
    ModelForm because the uniqueness constraint on the group's name causes errors to be
    raised whenever the name is not changed. And implementing the form as a "plain" Form
    is no harder.
    """

    name = forms.CharField(max_length=100, label="Group name")
    desired_instruments=forms.ModelMultipleChoiceField(queryset=Instrument.objects.all(),
                                                       widget=forms.CheckboxSelectMultiple(),
                                                       label="Desired instruments",
                                                       required=False)    


class InvitationForm(forms.ModelForm):
    """
    A form for sending an invitation to a user to join an already-existing group
    """
    def __init__(self, *args, **kwargs):
        instr = kwargs.pop("instr", None)
        # allow possibility to exclude fields from form
        exclude = kwargs.pop("exclude", None)
        super(InvitationForm, self).__init__(*args, **kwargs)
        # remove "-----" options from ForeignKey fields
        self.fields["group"].empty_label = None
        self.fields["group"].widget.choices = self.fields["group"].choices
        self.fields["invited_instrument"].empty_label = None
        self.fields["invited_instrument"].widget.choices = self.fields["invited_instrument"].choices
        # need to add the invited_user field separately as an AutoCompleteField
        if instr:
            self.fields["invited_user"] = AutoCompleteField("user_playing_"+instr,
                                                            label="User to invite",
                                                            help_text=None)
        for field_name in exclude:
            try:
                del self.fields[field_name]
            except KeyError:
                # can't delete the invited_user field if it wasn't created -
                # but can just ignore this error
                pass

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


class GroupMessageForm(forms.ModelForm):
    """
    Form for posting a new message to a group's private forum. When used in practice, it
    will either be invoked from a specific thread, in which case it adds the new message
    to that thread - or it is invoked when starting a new thread.
    """
    def __init__(self, *args, **kwargs):
        # if a "new_thread" kwarg is passed, the message is used to start a new thread,
        # and therefore needs a "name" field
        new = kwargs.pop("new_thread", None)
        super(GroupMessageForm, self).__init__(*args, **kwargs)
        if new:
            self.fields["name"] = forms.CharField(max_length=200)
    
    class Meta:
        model = GroupMessage
        fields = ["message"]
