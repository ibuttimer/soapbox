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
        user[0].lower(): {
            User.FIRST_NAME_FIELD: user[0],
            User.LAST_NAME_FIELD: user[1],
            User.USERNAME_FIELD: user[2],
            User.PASSWORD_FIELD: user[3],
            User.EMAIL_FIELD: user[4],
            User.AVATAR_FIELD: user[5],
            User.BIO_FIELD: user[6],
        } for user in [
            ("Joe", "Know_it_all", "joe.knowledge.all",
             "more-than-8-not-like-user", "ask.joe@knowledge.all",
             "flattering-pic.jpg", "The man in the know"),
            ("Jill", "Know_a_bit", "jill.knowledge.some",
             "more-than-8-on-a-plate", "ask.jill@knowledge.some",
             "nice-pic.jpg", "The woman to ask")
        ]
    }

    @staticmethod
    def create_users() -> dict:
        """
        Create test users
        :return: dict of test users
        """
        return {
            key: User.objects.create(**BaseUserTest.USER_INFO[key])
            for key in BaseUserTest.USER_INFO
        }

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        cls.users = BaseUserTest.create_users()

    @classmethod
    def get_user_by_index(cls, index: int) -> tuple[User, str]:
        """
        Get a test user by key index
        :param index: key index
        :return: tuple of user and key
        """
        key = cls.get_user_key(index)
        return cls.users[key], key

    @classmethod
    def get_user_key(cls, index: int) -> str:
        """
        Get a test user key by index
        :param index: key index
        :return: key for user
        """
        return list(
            BaseUserTest.USER_INFO.keys()
        )[index % len(BaseUserTest.USER_INFO)]

    @staticmethod
    def num_users():
        return len(BaseUserTest.USER_INFO)

    @staticmethod
    def login_user_by_key(test_instance, name: str | None = None) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        if name is None:
            name = BaseUserTest.get_user_key(0)
        user = test_instance.users[name.lower()]
        test_instance.assertIsNotNone(user)
        test_instance.client.force_login(user)
        return user

    @staticmethod
    def login_user_by_id(test_instance, pk: int) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param pk: id of user to login
        :returns logged-in user
        """
        users = list(
            filter(lambda u: u.id == pk, test_instance.users.values())
        )
        test_instance.assertEqual(len(users), 1)
        user = users[0]
        test_instance.assertIsNotNone(user)
        test_instance.client.force_login(user)
        return user
