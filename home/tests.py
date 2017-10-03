# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response
import home.views

# Create your tests here.
class HomePageTest(TestCase):
    """very simple tests for homepage"""
    def test_home_page_resolves(self):
        """check that the view function is correctly wired to the URL"""
        home_page = resolve("/")
        self.assertEqual(home_page.func, home.views.home)

    def test_status_is_ok(self):
        """check that we get a 200 status"""
        home_page = self.client.get("/")
        self.assertEqual(home_page.status_code, 200)

    def test_content_is_correct(self):
        """check that the correct template is rendered"""
        home_page = self.client.get("/")
        self.assertTemplateUsed(home_page, "home/home.html")
        home_page_template_output = render_to_response("home/home.html", {"active": "home"}).content
        self.assertEqual(home_page.content, home_page_template_output)


class WhyPageTest(TestCase):
    """the same, for the "why" page"""
    def test_page_resolves(self):
        """check that the view function is correctly wired to the URL"""
        why_page = resolve("/why/")
        self.assertEqual(why_page.func, home.views.why)

    def test_status_is_ok(self):
        """check that we get a 200 status"""
        why_page = self.client.get("/why/")
        self.assertEqual(why_page.status_code, 200)

    def test_content_is_correct(self):
        """check that the correct template is rendered"""
        why_page = self.client.get("/why/")
        self.assertTemplateUsed(why_page, "home/why.html")
        why_page_template_output = render_to_response("home/why.html", {"active": "why"}).content
        self.assertEqual(why_page.content, why_page_template_output)
