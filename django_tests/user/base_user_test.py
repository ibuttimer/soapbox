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

import django

from user.models import User

# 'allauth' checks for 'django.contrib.sites', so django must be setup before
# test
os.environ.setdefault("ENV_FILE", ".test-env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soapbox.settings")
django.setup()

from django.test import TestCase    # noqa


class BaseUserTest(TestCase):
    """
    Base user test class
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
    }

    @staticmethod
    def create_user() -> User:
        """
        Create test user
        :return: test user
        """
        return User.objects.create(**BaseUserTest.USER_INFO)

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        cls.user = BaseUserTest.create_user()

    @staticmethod
    def login_user(test_instance):
        """
        Login user
        :param test_instance: instance of user test case
        """
        test_instance.assertIsNotNone(test_instance.user)
        test_instance.client.force_login(test_instance.user)
