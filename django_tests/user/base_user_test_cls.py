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
from typing import Optional

from django.test import TestCase
import django_tests.check_setup     # do env checks and setup
from user.models import User
from user.permissions import add_to_authors, add_to_moderators
from user.queries import is_moderator, is_author


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
            ("Ana", "Know_a_bit", "ana.knowledge.some",
             "more-than-8-on-a-plate", "ask.ana@knowledge.some",
             "nice-pic.jpg", "The woman to ask"),
            ("Mod", "Er_ate", "mod.er.ate",
             "more-than-8-playing-gate", "mod.it@fingers.button",
             "looking-stern-pic.jpg", "The guy with his finger on the button"),
        ]
    }
    MODERATOR_USERNAME = "mod"

    users: dict[str, User]
    authors: dict[str, User]
    moderators: dict[str, User]

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
        cls.authors = {}
        cls.moderators = {}
        for user in cls.users.values():
            if user.username == cls.MODERATOR_USERNAME:
                add_to_moderators(user)
                cls.moderators.update(**{
                    user.username: user
                })
            else:
                add_to_authors(user)
                cls.authors.update(**{
                    user.username: user
                })

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

    @classmethod
    def get_other_user(cls, not_this_user: User, moderator: bool = False):
        """
        Get a user other than the specified user
        :param not_this_user: user to not get
        :param moderator: is moderator flag; default False
        :return: another user
        """
        for user_idx in range(len(cls.users)):
            user, _ = cls.get_user_by_index(user_idx)
            if user != not_this_user:
                if moderator and is_moderator(user):
                    break
                else:
                    break
        else:
            raise ValueError(
                f'{"Moderator" if moderator else "User"} other than '
                f'{not_this_user} not found')
        return user

    @classmethod
    def get_user(cls, moderator: bool = False, author: bool = False):
        """
        Get a user
        :param moderator: is moderator flag; default False
        :param author: is author flag; default False
        :return: another user
        """
        for user_idx in range(len(cls.users)):
            user, _ = cls.get_user_by_index(user_idx)
            if moderator and is_moderator(user):
                break
            elif author and is_author(user):
                break
        else:
            raise ValueError(
                f'{"Moderator" if moderator else "User"} not found')
        return user

    @classmethod
    def num_users(cls):
        """ Get number of users """
        return len(cls.users)

    @classmethod
    def num_authors(cls):
        """ Get number of authors """
        return len(cls.authors)

    @classmethod
    def num_moderators(cls):
        """ Get number of moderators """
        return len(cls.moderators)

    @staticmethod
    def login_user(test_instance: TestCase, user: User) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param user: user to login
        :returns logged-in user
        """
        test_instance.assertIsNotNone(user)
        test_instance.client.force_login(user)
        return user

    @staticmethod
    def login_user_by_key(
            test_instance: TestCase, name: Optional[str] = None) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        if name is None:
            name = BaseUserTest.get_user_key(0)
        user = test_instance.users[name.lower()]
        return test_instance.login_user(test_instance, user)

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
        return BaseUserTest.login_user(test_instance, user)
