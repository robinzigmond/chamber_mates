# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from models import Profile, Distance, Instrument, Standard, UserInstrument


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


class ProfileTest(TestCase):
    """
    Tests regarding the profile form
    """
    def test_data_saved_correctly_when_profile_added(self):
        """
        Simulate submission of the profile form, and check that the database is updated
        as expected
        """
        # this test does not currently work, mainly I think because I am not submitting
        # the data correctly in the simulated POST request. I intend to come back to this
        # later!

        # as before, create new user
        self.client.post("/register/", {"username": "user", "email": "address@example.com",
                                        "password1": "secretpwd", "password2": "secretpwd"})
        my_user = User.objects.get(username="user")
        # create profile instance attached to above user (who is now logged in,
        # after registering)
        fifty_miles = Distance.objects.create(distance=50)
        professional = Standard.objects.create(standard="professional")
        violin = Instrument.objects.create(instrument="violin")
        piano = Instrument.objects.create(instrument="piano")
        new_violin = UserInstrument.objects.create(instrument=violin, standard=professional,
                                                   desired_instruments=[piano, violin],
                                                   accepted_standards=[professional])(False).pk
        new_piano = UserInstrument.objects.create(instrument=piano, standard=professional,
                                                   desired_instruments=[piano, violin],
                                                   accepted_standards=[professional])(False).pk
        # create profile
        resp = self.client.post("/profile/edit/", {"email": "changed@example.com",
                                                   "current_password": "secretpwd",
                                                   "new_password1": "newpasswd",
                                                   "new_password2": "newpasswd",
                                                   "location": Point(-1, 53),
                                                   "max_distance": fifty_miles.pk,
                                                   "form-TOTAL_FORMS": 2,
                                                   "form-INITIAL_FORMS": 1,
                                                   "form-MAX_NUM_FORMS": 1000,
                                                   "form-0-instrument": violin.pk,
                                                   "form-0-standard": professional.pk,
                                                   "form-0-desired_instruments": [piano.pk, violin.pk],
                                                   "form-0-accepted_standards": [professional.pk],
                                                   "form-0-id": new_violin,
                                                   "form-1-instrument": piano,
                                                   "form-1-standard": professional.pk,
                                                   "form-1-desired_instruments": [piano.pk, violin.pk],
                                                   "form-1-accepted_standards": [professional.pk],
                                                   "form-1-id": new_piano})
        # check response
        # self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, "/dashboard/")
        # check profile data is saved correctly
        new_profile = Profile.objects.get(username="user")
        self.assertEqual(new_profile.user, my_user)
        self.assertEqual(new_profile.location, Point(-1, 53))
        self.assertEqual(new_profile.max_distance, fifty_miles)
        num_instruments = UserInstrument.objects.filter(user=my_user).count()
        self.assertEqual(num_instruments, 2)
