#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
import os
from http import HTTPStatus

import django
from django.http import HttpResponse
from django.urls import reverse
from bs4 import BeautifulSoup

from soapbox import USER_APP_NAME, USER_ID_ROUTE_NAME
from user.models import User

# 'allauth' checks for 'django.contrib.sites', so django must be setup before
# test
os.environ.setdefault("ENV_FILE", ".test-env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soapbox.settings")
django.setup()

from django.test import TestCase    # noqa


class TestProfileView(TestCase):
    """
    Test profile page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    USER_INFO = {
        User.FIRST_NAME_FIELD: "Joe",
        User.LAST_NAME_FIELD: "Know_it_all",
        User.USERNAME_FIELD: "joe.knowledge.all",
        User.PASSWORD_FIELD: "more-than-8-not-like-user",
        User.EMAIL_FIELD: "ask.joe@knowledge.all",
        User.AVATAR_FIELD: "flattering-pic.jpg",
        User.BIO_FIELD: "The man in the know",
        # User.CATEGORIES_FIELD: "" TODO user categories test
    }

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        cls.user = User.objects.create(**TestProfileView.USER_INFO)

    def login_user(self):
        """ Login user """
        self.assertIsNotNone(TestProfileView.user)
        self.client.force_login(TestProfileView.user)

    def get_profile(self) -> HttpResponse:
        """ Get the profile page """
        self.assertIsNotNone(TestProfileView.user)
        return self.client.get(
            reverse(USER_ID_ROUTE_NAME, args=[TestProfileView.user.id]))

    def test_not_logged_in_access_profile(self):
        """ Test must be logged in to access profile """
        response = self.get_profile()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_profile(self):
        """ Test profile page uses correct template """
        self.login_user()
        response = self.get_profile()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, f'{USER_APP_NAME}/profile.html')

    def test_profile_content(self):
        """ Test profile page content """
        self.login_user()
        response = self.get_profile()
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check h1 tags for username
        found = False
        for h1 in soup.find_all('h1'):
            found = TestProfileView.USER_INFO[User.USERNAME_FIELD] in h1.text
            if found:
                break
        self.assertTrue(found)

        # check input tags for first/last name and email
        inputs = [ip.get('value') for ip in soup.find_all('input')]
        for field in [User.FIRST_NAME_FIELD, User.LAST_NAME_FIELD,
                      User.EMAIL_FIELD]:
            with self.subTest(f'{field}'):
                found = False
                for ip in inputs:
                    found = TestProfileView.USER_INFO[field] == ip
                    if found:
                        break
                self.assertTrue(found)

        # check img tags for image
        found = False
        for img in soup.find_all('img'):
            found = TestProfileView.USER_INFO[User.AVATAR_FIELD] \
                    in img.get('src')
            if found:
                break
        self.assertTrue(found)

        # check textarea tags for bio
        found = False
        for textarea in soup.find_all('textarea'):
            found = TestProfileView.USER_INFO[User.BIO_FIELD] in textarea.text
            if found:
                break
        self.assertTrue(found)
