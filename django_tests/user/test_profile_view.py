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
from enum import Enum, auto
from http import HTTPStatus
from typing import Union

from bs4 import BeautifulSoup
from django.http import HttpResponse

from opinions.models import Category
from soapbox import USER_APP_NAME
from user.constants import USER_USERNAME_ROUTE_NAME
from utils import reverse_q, namespaced_url
from user import USER_ID_ROUTE_NAME
from user.models import User
from .base_user_test_cls import BaseUserTest
from ..category_mixin_test_cls import CategoryMixin
from ..soup_mixin import SoupMixin


class AccessBy(Enum):
    """ Access route class """
    BY_ID = auto()
    BY_USERNAME = auto()

    def identifier(self, user: User) -> Union[int, str]:
        """
        Get the identifier from `user` as specified by this access
        :param user: user to get identifier for
        :return: identifier
        """
        return user.id if self == AccessBy.BY_ID else user.username


class TestProfileView(SoupMixin, CategoryMixin, BaseUserTest):
    """
    Test profile page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestProfileView, cls).setUpTestData()
        # assign categories to users
        category_list = list(Category.objects.all())
        mod_num = 2
        for user in cls.users.values():
            user.categories.add(
                *[category for idx, category in enumerate(category_list)
                  if idx % mod_num]
            )
            mod_num += 1

    def login_user_by_key(self, name: str | None = None) -> User:
        """
        Login user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_key(self, name)

    def get_profile(self, user: User, access_by: AccessBy) -> HttpResponse:
        """
        Get the profile page
        :param user: user to get profile for
        :param access_by: access method
        """
        self.assertIsNotNone(user)
        return self.client.get(
            reverse_q(
                namespaced_url(
                    USER_APP_NAME,
                    USER_ID_ROUTE_NAME if access_by == AccessBy.BY_ID else
                    USER_USERNAME_ROUTE_NAME
                ),
                args=[access_by.identifier(user)]))

    def test_not_logged_in_access_profile(self):
        """ Test must be logged in to access profile """
        user, _ = TestProfileView.get_user_by_index(0)
        response = self.get_profile(user, AccessBy.BY_ID)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_profile(self):
        """ Test profile page uses correct template """
        user = self.login_user_by_key()
        response = self.get_profile(user, AccessBy.BY_ID)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, f'{USER_APP_NAME}/profile.html')

    def own_profile_content_test(self, access_by: AccessBy):
        """ Test profile page content for logged-in user """
        _, key = TestProfileView.get_user_by_index(0)
        user = self.login_user_by_key(key)
        response = self.get_profile(user, access_by)
        self.verify_profile_content(user, key, response)

    def other_profile_content_test(self, access_by: AccessBy):
        """ Test profile page content for not logged-in user """
        _, key = TestProfileView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        user, key = TestProfileView.get_user_by_index(1)

        self.assertNotEqual(logged_in_user, user)
        response = self.get_profile(user, access_by)
        self.verify_profile_content(user, key, response, is_readonly=True)

    def test_own_profile_content_by_id(self):
        """ Test profile page content for logged-in user by id """
        self.own_profile_content_test(AccessBy.BY_ID)

    def test_other_profile_content_by_id(self):
        """ Test profile page content for not logged-in user by id """
        self.other_profile_content_test(AccessBy.BY_ID)

    def test_own_profile_content_by_username(self):
        """ Test profile page content for logged-in user by username """
        self.own_profile_content_test(AccessBy.BY_USERNAME)

    def test_other_profile_content_username(self):
        """ Test profile page content for not logged-in user by username """
        self.other_profile_content_test(AccessBy.BY_USERNAME)

    def verify_profile_content(
                self, user: User, key: str, response: HttpResponse,
                is_readonly: bool = False
            ):
        """
        Verify profile page content for user
        :param user: user to check
        :param key: key for user
        :param response: profile response
        :param is_readonly: is readonly flag; default False
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check h1 tags for username
        TestProfileView.find_tag(self, soup.find_all('h1'),
                                 lambda tag: user.username in tag.text)

        # check input tags for first/last name and email
        for field in [user.FIRST_NAME_FIELD, User.LAST_NAME_FIELD,
                      User.EMAIL_FIELD]:
            with self.subTest(f'{field}'):
                expected = getattr(user, field)
                TestProfileView.find_tag(
                    self, soup.find_all('input'),
                    lambda tag: TestProfileView.equal_tag_attr(
                        tag, 'value', expected)
                )

        # check img tags for image
        TestProfileView.find_tag(
            self, soup.find_all('img'),
            lambda tag: TestProfileView.USER_INFO[key][User.AVATAR_FIELD]
            in tag.get('src'))

        # check for bio
        if is_readonly:
            # check for readonly_content div, can't check content as its
            # replaced by javascript
            self.find_tag(self, soup.find_all(id='readonly_content'),
                          lambda tag: True)
        else:
            # check textarea tags for content
            self.find_tag(self, soup.find_all('textarea'),
                          lambda tag: user.bio in tag.text)

        # check categories
        if is_readonly:
            TestProfileView.check_category_list(
                self, soup, user.categories.all())
        else:
            TestProfileView.check_category_options(
                self, soup, user.categories.all())

        # check read only
        self.check_tag(self, soup.find_all('fieldset'), is_readonly,
                       lambda tag: tag.has_attr('disabled'))
