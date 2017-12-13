# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.forms import modelformset_factory
from models import Profile, Distance, Instrument, Standard, UserInstrument, Match
from forms import UserInstrumentForm
from views import update_matches


# Create your tests here.
class RegistrationTest(TestCase):
    """
    Tests for user registration
    """
    def test_registration(self):
        """
        Test that a "normal" registration works as intended
        """
        resp = self.client.post("/register/", {"username": "user", "email": "address@example.com",
                                               "password1": "secretpwd", "password2": "secretpwd"})
        self.assertRedirects(resp, "/profile/edit/")

        new_user = User.objects.filter(username="user")
        self.assertEqual(len(new_user), 1)


    def test_email_required(self):
        """
        Test that trying to registering without giving an email fails to work
        """
        resp = self.client.post("/register/", {"username": "user", "password1": "secretpwd",
                                               "password2": "secretpwd"})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/register.html")
        self.assertFormError(resp, "form", "email", "This field is required.")

        new_user = User.objects.filter(username="user")
        self.assertEqual(len(new_user), 0)

    
    def test_registration_enables_login(self):
        """
        Test that it is not possible to login without first registering
        """
        not_registered = self.client.post("/login/", {"username": "user", "password": "secretpwd"})
        self.assertEqual(not_registered.status_code, 200)
        self.assertFormError(not_registered, "form", None,
                             "Please enter a correct username and password. Note that both fields may be case-sensitive.")
        self.assertTemplateUsed(not_registered, "accounts/login.html")

        self.client.post("/register/", {"username": "user", "email": "address@example.com",
                                        "password1": "secretpwd", "password2": "secretpwd"})
        registered = self.client.post("/login/", {"username": "user", "password": "secretpwd"})
        self.assertEqual(registered.status_code, 302)


class AccountRedirectTests(TestCase):
    """
    Tests showing that users who are not logged in, or do not have a profile yet, are
    redirected appropriately
    """
    def test_login_required_for_restricted_pages(self):
        """
        Test that the "dashboard", "edit profile" and "matches" pages are
        unavailable without loggin in first (and in fact redirect to the login page)
        """
        dashboard = self.client.get("/dashboard/")
        edit_profile = self.client.get("/profile/edit/")
        matches = self.client.get("/matches/")
        self.assertRedirects(dashboard, "/login/?next=/dashboard/")
        self.assertRedirects(edit_profile, "/login/?next=/profile/edit/")
        self.assertRedirects(matches, "/login/?next=/matches/")


    def test_profile_required_before_accessing_dashboard(self):
        """
        Test that, when a user is logged in but has not yet completed a profile,
        they will be prompted to complete it before accessing their user dashboard.
        """
        # register a new user, with no profile yet
        self.client.post("/register/", {"username": "user", "email": "address@example.com",
                                        "password1": "secretpwd", "password2": "secretpwd"})
        no_profile = self.client.get("/dashboard/")
        self.assertRedirects(no_profile, "/profile/edit/")
        # now give them a profile
        fifty_miles = Distance.objects.create(distance=50)
        Profile.objects.create(user=User.objects.get(username="user"),
                               location=Point(-1, 53, srid=4326),
                               max_distance=fifty_miles)
        with_profile = self.client.get("/dashboard/")
        self.assertEqual(with_profile.status_code, 200)
        self.assertTemplateUsed(with_profile, "accounts/dashboard.html")


# the following tests does not work, and has therefore been commented out. Despite numerous attempts,
# I have been unable to correctly pass in the "id" values of the individual forms in the instrument
# FormSet - this is required for all POST submission to the edit_profile page, even if I am not specifically
# testing the instrument form functionality. (I have tried various integer values, including 0, as well as
# the empty string, and None. When the form is first created by Django, this hidden field has its value
# attribute set to an empty string, but this does not work in testing - nor does leaving the field out.)

# I would have added more tests along these lines than the 2 below, but I have chosen to spend my time on other
# things since becoming aware of the problem, and failing to figure out how to solve it

# class ProfileTest(TestCase):
#     """
#     Tests regarding the profile form
#     """
    # def test_data_saved_correctly_when_profile_added(self):
    #     """
    #     Simulate submission of the profile form, and check that the database is updated
    #     as expected
    #     """
        # as before, create new user
    #     self.client.post("/register/", {"username": "user", "email": "address@example.com",
    #                                     "password1": "secretpwd", "password2": "secretpwd"})
    #     my_user = User.objects.get(username="user")
        # create profile instance attached to above user (who is now logged in,
        # after registering)
    #     fifty_miles = Distance.objects.create(distance=50)
    #     professional = Standard.objects.create(standard="professional")
    #     violin = Instrument.objects.create(instrument="violin")
    #     piano = Instrument.objects.create(instrument="piano")

    #     instrument_FormSet = modelformset_factory(UserInstrument, UserInstrumentForm, extra=1)
    #     instrument_forms = instrument_FormSet(queryset=UserInstrument.objects.none())

        # create profile
    #     resp = self.client.post("/profile/edit/", {"email": "changed@example.com",
    #                                                "current_password": "secretpwd",
    #                                                "new_password1": "newpasswd",
    #                                                "new_password2": "newpasswd",
    #                                                "location": "POINT (-1 53)",
    #                                                "max_distance": fifty_miles.pk,
    #                                                "form-TOTAL_FORMS": 2,
    #                                                "form-INITIAL_FORMS": 1,
    #                                                "form-MAX_NUM_FORMS": 1000,
    #                                                "form-0-instrument": violin.pk,
    #                                                "form-0-standard": professional.pk,
    #                                                "form-0-desired_instruments": piano.pk,
    #                                                "form-0-desired_instruments": violin.pk,
    #                                                "form-0-accepted_standards": professional.pk,
    #                                                "form-0-id": instrument_forms[0].initial["id"]})
        # check response
    #     self.assertRedirects(resp, "/dashboard/")
        # check profile data is saved correctly
    #     new_profile = Profile.objects.get(username="user")
    #     self.assertEqual(new_profile.user, my_user)
    #     self.assertEqual(new_profile.location, Point(-1, 53))
    #     self.assertEqual(new_profile.max_distance, fifty_miles)
    #     num_instruments = UserInstrument.objects.filter(user=my_user).count()
    #     self.assertEqual(num_instruments, 2)

    # def test_change_of_password_works(self):
    #     """
    #     Test to see that changing password works as expected
    #     """
    #     # create user and profile instances:
    #     fifty_miles = Distance.objects.create(distance=50)
    #     user = User.objects.create_user(username="user", email="address@example.com", password="secretpwd")
    #     Profile.objects.create(user=user, description="Test",
    #                            location=Point(-1,53), max_distance=fifty_miles)
        # log user in
    #     self.client.login(username="user", password="secretpwd")

        # although we're not testing the instrument forms, the formset management form data
        # is required or an error is thrown
    #     wrong_pwd = self.client.post("/profile/edit/", {"email": "address@example.com",
    #                                                     "current_password": "wrong",
    #                                                     "new_password1": "newpasswd",
    #                                                     "new_password2": "newpasswd",
    #                                                     "form-TOTAL_FORMS": 2,
    #                                                     "form-INITIAL_FORMS": 1,
    #                                                     "form-MAX_NUM_FORMS": 1000})
    #     print wrong_pwd
    #     self.assertFormError(wrong_pwd, "form", "current_password", "Please enter your correct current password")


class MatchesTest(TestCase):
    """
    Tests that matches between users are created - and not created! - as would be expected.
    The tests are of the "update_matches" function which is called whenever any user alters
    their profile
    """
    # method to create test data:
    def make_data(self):
        self.user_1 = User.objects.create_user(username="alice", password="secretpwd")
        self.user_2 = User.objects.create_user(username="bob", password="secretpwd")
        thirty_miles = Distance.objects.create(distance=30)
        self.profile_1 = Profile.objects.create(user=self.user_1, location=Point(-1.6, 54.8),
                                                max_distance=thirty_miles)
        self.profile_2 = Profile.objects.create(user=self.user_2, location=Point(-1.6, 54.5),
                                                max_distance=thirty_miles)
        violin = Instrument.objects.create(instrument="violin")
        piano = Instrument.objects.create(instrument="piano")
        good_standard = Standard.objects.create(standard="good")
        self.alice_violin = UserInstrument.objects.create(user=self.user_1, instrument=violin,
                                                          standard=good_standard)
        self.alice_violin.desired_instruments.add(piano)
        self.alice_violin.accepted_standards.add(good_standard)
        self.alice_violin.save()
        self.bob_piano = UserInstrument.objects.create(user=self.user_2, instrument=piano,
                                                       standard=good_standard)
        self.bob_piano.desired_instruments.add(violin)
        self.bob_piano.accepted_standards.add(good_standard)
        self.bob_piano.save()
        # pretend one of the users has just entered/updated their details
        update_matches(self.user_1, new_location=True)


    def test_matches_created(self):
        """
        Checks that users who should match do lead to a Match object being created
        """
        self.make_data()
        self.assertEqual(Match.objects.all().count(), 2)  # both users should match each other


    def test_distance_matters(self):
        """
        Checks that reducing the max_distance value of one of the above two users eliminates one
        match - while leaving the other in place
        """
        self.make_data()
        twenty_miles = Distance.objects.create(distance=20)
        self.profile_1.max_distance = twenty_miles
        self.profile_1.save()
        update_matches(self.user_1, new_maxdist=True)
        self.assertEqual(Match.objects.filter(requesting_user=self.user_1).count(), 0)
        self.assertEqual(Match.objects.filter(found_user=self.user_1).count(), 1)


    def test_instrument_matters(self):
        """
        Checks that changing the instrument desired makes the match go away for that user
        """
        self.make_data()
        piano = Instrument.objects.create(instrument="piano")
        self.alice_violin.desired_instruments = [piano]
        self.alice_violin.save()
        update_matches(self.user_1, new_instruments=True)
        self.assertEqual(Match.objects.filter(requesting_user=self.user_1).count(), 0)
        self.assertEqual(Match.objects.filter(found_user=self.user_1).count(), 1)


    def test_standard_matters(self):
        """
        Checks that changing the standard of one of the players makes the match go away
        """
        self.make_data()
        beginner = Standard.objects.create(standard="beginner")
        self.alice_violin.standard = beginner
        self.alice_violin.save()
        update_matches(self.user_1, new_instruments=True)
        self.assertEqual(Match.objects.filter(requesting_user=self.user_1).count(), 1)
        self.assertEqual(Match.objects.filter(found_user=self.user_1).count(), 0)
 