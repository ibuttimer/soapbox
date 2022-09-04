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
from .base_user_test_cls import BaseUserTest


class TestProfileView(BaseUserTest):
    """
    Test profile page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestProfileView, TestProfileView).setUpTestData()
        # assign categories to users
        category_list = list(Category.objects.all())
        mod_num = 2
        for user in cls.users.values():
            user.categories.add(
                *[category for idx, category in enumerate(category_list)
                  if idx % mod_num]
            )
            mod_num += 1

    def login_user(self, name: str | None = None) -> User:
        """
        Login user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseUserTest.login_user(self, name)

    def get_profile(self, user: User) -> HttpResponse:
        """
        Get the profile page
        :param user - user to get profile for
        """
        self.assertIsNotNone(user)
        return self.client.get(
            reverse(USER_ID_ROUTE_NAME, args=[user.id]))

    def test_not_logged_in_access_profile(self):
        """ Test must be logged in to access profile """
        user, _ = TestProfileView.get_user_by_index(0)
        response = self.get_profile(user)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_profile(self):
        """ Test profile page uses correct template """
        user = self.login_user()
        response = self.get_profile(user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, f'{USER_APP_NAME}/profile.html')

    def test_own_profile_content(self):
        """ Test profile page content for logged-in user"""
        _, key = TestProfileView.get_user_by_index(0)
        user = self.login_user(key)
        response = self.get_profile(user)
        self.verify_profile_content(user, key, response)

    def test_other_profile_content(self):
        """ Test profile page content for not logged-in user"""
        _, key = TestProfileView.get_user_by_index(0)
        logged_in_user = self.login_user(key)

        user, key = TestProfileView.get_user_by_index(1)

        self.assertNotEqual(logged_in_user, user)
        response = self.get_profile(user)
        self.verify_profile_content(user, key, response, is_readonly=True)

    def verify_profile_content(
                self, user: User, key: str, response: HttpResponse,
                is_readonly: bool = False
            ):
        """
        Verify profile page content for user
        :param user: user to to check
        :param key: key for user
        :param response: profile response
        :param is_readonly: is readonly flag; default False
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check h1 tags for username
        found = False
        for h1 in soup.find_all('h1'):
            found = user.username in h1.text
            if found:
                break
        self.assertTrue(found)

        # check input tags for first/last name and email
        inputs = [ip.get('value') for ip in soup.find_all('input')]
        for field in [user.FIRST_NAME_FIELD, User.LAST_NAME_FIELD,
                      User.EMAIL_FIELD]:
            with self.subTest(f'{field}'):
                found = False
                for ip in inputs:
                    found = TestProfileView.USER_INFO[key][field] == ip
                    if found:
                        break
                self.assertTrue(found)

        # check img tags for image
        found = False
        for img in soup.find_all('img'):
            found = TestProfileView.USER_INFO[key][User.AVATAR_FIELD] \
                    in img.get('src')
            if found:
                break
        self.assertTrue(found)

        # check textarea tags for bio
        found = False
        for textarea in soup.find_all('textarea'):
            found = user.bio in textarea.text
            if found:
                break
        self.assertTrue(found)

        # check categories
        category_options = [
            opt for opt in soup.find_all(
                lambda tag: tag.name == 'option'
                and tag.has_attr('selected')
                and tag.parent.name == 'select'
            )]
        for category in list(user.categories.all()):
            with self.subTest(f'category {category}'):
                tags = list(
                    filter(
                        lambda opt:
                        category.id == int(opt['value']) and
                        category.name == opt.text,
                        category_options
                    )
                )
                self.assertEqual(len(tags), 1)

        # check read only
        bingo = False
        for fieldset in soup.find_all('fieldset'):
            if is_readonly and fieldset.has_attr('disabled'):
                bingo = True
            elif not is_readonly and not fieldset.has_attr('disabled'):
                bingo = True
            break
        self.assertTrue(bingo)
