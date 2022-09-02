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

from soapbox import BASE_APP_NAME
from user.models import User

# 'allauth' checks for 'django.contrib.sites', so django must be setup before
# test
os.environ.setdefault("ENV_FILE", ".test-env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soapbox.settings")
django.setup()

from django.test import TestCase    # noqa


class TestHome(TestCase):
    """
    Test profile page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    USER_INFO = {
        User.FIRST_NAME_FIELD: "Joe",
        User.LAST_NAME_FIELD: "Know_it_all",
        User.USERNAME_FIELD: "joe.knowledge.all",
        User.PASSWORD_FIELD: "more-than-8-not-like-user",
    }

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        cls.user = User.objects.create(**TestHome.USER_INFO)

    def login_user(self):
        """ Login user """
        self.assertIsNotNone(TestHome.user)
        self.client.force_login(TestHome.user)

    def get_home(self) -> HttpResponse:
        """ Get the home page """
        self.assertIsNotNone(TestHome.user)
        return self.client.get('/')

    def test_get_home(self):
        """ Test home page uses correct template """
        self.login_user()
        response = self.get_home()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, f'{BASE_APP_NAME}/home.html')

    def test_home_content(self):
        """ Test home page content """
        self.login_user()
        response = self.get_home()
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # get all hrefs on page
        hrefs = [link.get('href') for link in soup.find_all('a')]

        for route in ["account_logout"]:
            with self.subTest(f'route {route}'):
                url = reverse(route)
                self.assertIsNotNone(url)
                self.assertIn(url, hrefs)
