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
from http import HTTPStatus

from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.urls import reverse

from soapbox import USER_APP_NAME, USER_ID_ROUTE_NAME
from user.models import User
from opinions.models import Category
from .base_user_test import BaseUserTest


class TestProfileView(BaseUserTest):
    """
    Test profile page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestProfileView, TestProfileView).setUpTestData()
        # assign categories to user
        category_list = list(Category.objects.all())
        cls.user.categories.add(
            *[category for idx, category in enumerate(category_list)
              if idx % 2]
        )

    def login_user(self):
        """ Login user """
        BaseUserTest.login_user(self)

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

        # TODO check categories
