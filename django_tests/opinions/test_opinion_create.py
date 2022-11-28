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

from bs4 import BeautifulSoup, Tag
from django.http import HttpResponse

from categories import (
    STATUS_DRAFT, CATEGORY_UNASSIGNED
)
from categories.models import Category
from opinions import (
    OPINION_NEW_ROUTE_NAME
)
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from ..soup_mixin import SoupMixin
from ..user.base_user_test import BaseUserTest

OPINION_FORM_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_form.html'


class TestOpinionCreate(SoupMixin, BaseUserTest):
    """
    Test opinion create page
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionCreate, cls).setUpTestData()

    def login_user_by_key(self, name: str | None = None) -> User:
        """
        Login user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_key(self, name)

    def login_user_by_id(self, pk: int) -> User:
        """
        Login user
        :param pk: id of user to login
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_id(self, pk)

    def get_opinion(self) -> HttpResponse:
        """
        Get the opinion create page
        """
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, OPINION_NEW_ROUTE_NAME)))

    def test_not_logged_in_access_opinion(self):
        """ Test must be logged in to access opinion """
        response = self.get_opinion()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_opinion(self):
        """ Test opinion page uses correct template """
        _, key = TestOpinionCreate.get_user_by_index(0)
        user = self.login_user_by_key(key)
        response = self.get_opinion()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_FORM_TEMPLATE)

    def test_get_own_opinion_content(self):
        """ Test page content for opinion of logged-in user"""
        _, key = TestOpinionCreate.get_user_by_index(0)
        user = self.login_user_by_key(key)
        response = self.get_opinion()
        self.verify_opinion_content(response)

    def verify_opinion_content(
            self, response: HttpResponse,
            is_readonly: bool = False
    ):
        """
        Verify opinion page content for user
        :param response: opinion response
        :param is_readonly: is readonly flag; default False
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check input tag for title
        # (in edit mode id is the auto id of the form field)
        inputs = soup.find_all(id='id_title')
        self.assertEqual(len(inputs), 1)

        # check textarea tags for content
        inputs = soup.find_all('textarea')
        self.assertEqual(len(inputs), 1)

        # check categories
        category_options = [
            opt for opt in soup.find_all(
                lambda tag: tag.name == 'option'
                and tag.has_attr('selected')
                and tag.parent.name == 'select'
            )]
        for category in [Category.objects.get(name=CATEGORY_UNASSIGNED)]:
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

        # check fieldset is disabled in read only mode
        self.check_tag(self, soup.find_all('fieldset'), is_readonly,
                       lambda tag: tag.has_attr('disabled'))

        # check status only displayed if not read only,
        # i.e. current user's opinion
        found = False
        for span in soup.find_all('span'):
            if SoupMixin.in_tag_attr(span, 'class', 'badge'):
                found = STATUS_DRAFT == span.text
                if found:
                    break
        if is_readonly:
            self.assertFalse(found)
        else:
            self.assertTrue(found)

        # check submit button only displayed in not read only mode
        tags = soup.find_all(is_submit_button)
        if is_readonly:
            self.assertEqual(len(tags), 0)
        else:
            self.assertEqual(len(tags), 3)


def is_submit_button(tag: Tag):
    """
    Check `tag` is an opinion submit button
    :param tag: tag to check
    :return: True is opinion submit button, otherwise False
    """
    return tag.name == 'button' \
        and SoupMixin.equal_tag_attr(tag, 'type', 'submit') \
        and SoupMixin.in_tag_attr(tag, 'class', 'btn__submit-opinion')
