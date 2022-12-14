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

from django_tests.user.base_user_test_cls import BaseUserTest
from soapbox import OPINIONS_APP_NAME


class TestHome(BaseUserTest):
    """
    Test profile page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def user_login(self):
        """ Login user """
        user, _ = self.get_user_by_index(0)
        self.login_user(self, user)

    def get_home(self) -> HttpResponse:
        """ Get the home page """
        return self.client.get('/', follow=True)

    def test_get_home(self):
        """ Test home page uses correct template """
        self.user_login()
        response = self.get_home()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response,
                                f'{OPINIONS_APP_NAME}/opinion_feed.html')

    def test_home_content(self):
        """ Test home page content """
        self.user_login()
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
