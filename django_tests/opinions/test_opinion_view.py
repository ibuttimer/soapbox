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
import json
import re
from http import HTTPStatus

from bs4 import BeautifulSoup
from django.http import HttpResponse

from categories import (
    STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED
)
from categories.models import Status
from opinions import (
    OPINION_ID_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_ROUTE_NAME, OPINION_STATUS_ID_ROUTE_NAME
)
from opinions.constants import STATUS_QUERY
from opinions.models import Opinion
from opinions.views_utils import QueryStatus
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q
from .base_opinion_test_cls import BaseOpinionTest
from .test_opinion_create import check_submit_button, OPINION_FORM_TEMPLATE
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test_cls import BaseUserTest

OPINION_VIEW_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_view.html'

# query params to match BaseOpinionTest.STATUSES
QUERY_PARAMS = {
    STATUS_DRAFT: QueryStatus.DRAFT,
    STATUS_PREVIEW: QueryStatus.PREVIEW,
    STATUS_PUBLISHED: QueryStatus.PUBLISH,
}

BY_ID = 'id'
BY_SLUG = 'slug'


class TestOpinionView(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionView, TestOpinionView).setUpTestData()

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

    def get_opinion_by_id(self, pk: int) -> HttpResponse:
        """
        Get the opinion page
        :param pk: id of opinion
        """
        return self.client.get(
            reverse_q(OPINION_ID_ROUTE_NAME, args=[pk]))

    def get_opinion_by_slug(self, slug: str) -> HttpResponse:
        """
        Get the opinion page
        :param slug: slug of opinion
        """
        return self.client.get(
            reverse_q(OPINION_SLUG_ROUTE_NAME, args=[slug]))

    def get_opinion_by(
            self, identifier: [int, str], opinion_by: str) -> HttpResponse:
        """
        Get the opinion page
        :param identifier: opinion identifier
        :param opinion_by: method of accessing opinion; 'id' or 'slug'
        :returns response
        """
        get_by = self.get_opinion_by_id \
            if opinion_by == BY_ID else self.get_opinion_by_slug
        return get_by(identifier)

    def get_opinion_preview(self, pk: int) -> HttpResponse:
        """
        Get the opinion preview page
        :param pk: id of opinion
        """
        return self.client.get(
            reverse_q(OPINION_PREVIEW_ID_ROUTE_NAME, args=[pk]))

    def test_not_logged_in_access_by_id(self):
        """ Test must be logged in to access opinion by id """
        response = self.get_opinion_by(TestOpinionView.opinions[0].id, BY_ID)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_logged_in_access_by_slug(self):
        """ Test must be logged in to access opinion by slug """
        response = self.get_opinion_by(
            TestOpinionView.opinions[0].slug, BY_SLUG)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def check_get_own_opinion(self, opinion_by: str):
        """
        Test access to own opinions
        :param opinion_by: method of accessing opinion; 'id' or 'slug'
        """
        opinion = TestOpinionView.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        for status in [STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED]:
            with self.subTest(f'{opinion_by} - status {status}'):
                # get list of own opinions
                opinions = self.get_own_opinions(user, status)
                opinion = opinions[0]

                response = self.get_opinion_by(
                    opinion.id if opinion_by == BY_ID else opinion.slug,
                    opinion_by)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, OPINION_FORM_TEMPLATE)
                self.verify_opinion_content(opinion, response)

    def test_get_own_opinion_by_id(self):
        """ Test page content for opinion by id of logged-in user """
        self.check_get_own_opinion(BY_ID)

    def test_get_own_opinion_by_slug(self):
        """ Test page content for opinion by slug of logged-in user """
        self.check_get_own_opinion(BY_SLUG)

    def get_own_opinions(
            self, me: User, status: str) -> list[Opinion]:
        """
        Get a list of users' opinions with the specified status
        :param me: user to
        :param status: required status
        :return: list of opinions
        """
        # get list of users' published opinions
        opinions = list(
            filter(lambda op: op.user.id == me.id
                   and op.status.name == status,
                   TestOpinionView.opinions)
        )
        self.assertGreaterEqual(
            len(opinions), 1, msg=f'No opinions with {status} status')
        return opinions

    def get_other_users_opinions(
            self, not_me: User, status: str) -> list[Opinion]:
        """
        Get a list of other users' opinions with the specified status
        :param not_me: user to
        :param status: required status
        :return: list of opinions
        """
        # get list of other users' published opinions
        opinions = list(
            filter(lambda op: op.user.id != not_me.id
                   and op.status.name == status,
                   TestOpinionView.opinions)
        )
        self.assertGreaterEqual(
            len(opinions), 1, msg=f'No opinions with {status} status')
        return opinions

    def test_get_other_opinion_by_id(self):
        """ Test page content for opinion by id of not logged-in user """
        _, key = TestOpinionView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        # get list of other users' published opinions
        opinions = self.get_other_users_opinions(
            logged_in_user, STATUS_PUBLISHED)
        opinion = opinions[0]

        self.assertNotEqual(logged_in_user, opinion.user)
        response = self.get_opinion_by_id(opinion.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_VIEW_TEMPLATE)
        self.verify_opinion_content(opinion, response, is_readonly=True)

    def test_get_other_opinion_by_slug(self):
        """ Test page content for opinion by slug of not logged-in user """
        _, key = TestOpinionView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        # get list of other users' published opinions
        opinions = self.get_other_users_opinions(
            logged_in_user, STATUS_PUBLISHED)
        opinion = opinions[0]

        self.assertNotEqual(logged_in_user, opinion.user)
        response = self.get_opinion_by_slug(opinion.slug)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_VIEW_TEMPLATE)
        self.verify_opinion_content(opinion, response, is_readonly=True)

    def check_other_opinion_access(self, opinion_by: str):
        """
        Test access to unpublished opinions by id of not logged-in user
        :param opinion_by: method of accessing opinion; 'id' or 'slug'
        """
        _, key = TestOpinionView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        for status in [STATUS_DRAFT, STATUS_PREVIEW]:
            with self.subTest(f'{opinion_by} - status {status}'):
                # get list of other users' opinions
                opinions = self.get_other_users_opinions(
                    logged_in_user, status)
                opinion = opinions[0]

                self.assertNotEqual(logged_in_user, opinion.user)
                response = self.get_opinion_by_id(opinion.id) \
                    if opinion_by == BY_ID else \
                    self.get_opinion_by_slug(opinion.slug)
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_other_opinion_access_by_id(self):
        """
        Test access to unpublished opinions by id of not logged-in user
        """
        self.check_other_opinion_access(BY_ID)

    def test_get_other_opinion_access_by_slug(self):
        """
        Test access to unpublished opinions by slug of not logged-in user
        """
        self.check_other_opinion_access(BY_SLUG)

    def test_get_own_opinion_preview(self):
        """
        Test access to preview of own opinions
        """
        opinion = TestOpinionView.opinions[0]
        logged_in_user = self.login_user_by_id(opinion.user.id)

        for status in [STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED]:
            with self.subTest(f'status {status}'):
                # get list of own opinions
                opinions = self.get_own_opinions(logged_in_user, status)
                opinion = opinions[0]

                self.assertEqual(logged_in_user, opinion.user)
                response = self.get_opinion_preview(opinion.id)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, OPINION_VIEW_TEMPLATE)
                self.verify_opinion_content(
                    opinion, response, is_readonly=True, is_preview=True)

    def test_get_other_opinion_preview(self):
        """
        Test access to preview of others opinions
        """
        opinion = TestOpinionView.opinions[0]
        logged_in_user = self.login_user_by_id(opinion.user.id)

        for status in [STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED]:
            with self.subTest(f'status {status}'):
                # get list of other users' opinions
                opinions = self.get_other_users_opinions(
                    logged_in_user, status)
                self.assertGreaterEqual(len(opinions), 1)
                opinion = opinions[0]

                self.assertNotEqual(logged_in_user, opinion.user)
                response = self.get_opinion_preview(opinion.id)
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_own_opinion_status_patch(self):
        """
        Test access to setting status of own opinions
        """
        opinion = TestOpinionView.opinions[0]
        logged_in_user = self.login_user_by_id(opinion.user.id)
        self.assertEqual(logged_in_user, opinion.user)

        # get statuses and sort so current is last in list in order to
        # return opinion to initial state
        statuses = list(
            Status.objects.filter(name__in=BaseOpinionTest.STATUSES)
        )
        statuses.sort(key=lambda s: 1 if s == opinion.status else 0)

        query_params = list(map(lambda s: QUERY_PARAMS[s.name], statuses))

        for index in range(len(statuses)):
            status = statuses[index]
            with self.subTest(f'status {status}'):
                url = reverse_q(
                    OPINION_STATUS_ID_ROUTE_NAME, args=[opinion.id],
                    query_kwargs={
                        STATUS_QUERY: query_params[index].arg
                    })
                response = self.client.patch(url)
                result = json.loads(response.content)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(result['status'], status.name)

    def test_other_opinion_status_patch(self):
        """
        Test access to setting status of other users' opinions
        """
        opinion = TestOpinionView.opinions[0]
        logged_in_user = self.login_user_by_id(opinion.user.id)
        self.assertEqual(logged_in_user, opinion.user)

        # get list of other users' opinions
        opinions = self.get_other_users_opinions(
            logged_in_user, STATUS_DRAFT)
        self.assertGreaterEqual(len(opinions), 1)
        opinion = opinions[0]

        # get statuses and sort so current is last in list in order to
        # return opinion to initial state
        statuses = list(
            Status.objects.filter(name__in=BaseOpinionTest.STATUSES)
        )
        statuses.sort(key=lambda s: 1 if s == opinion.status else 0)

        query_params = list(map(lambda s: QUERY_PARAMS[s.name], statuses))

        for index in range(len(statuses)):
            status = statuses[index]
            with self.subTest(f'status {status}'):
                url = reverse_q(
                    OPINION_STATUS_ID_ROUTE_NAME, args=[opinion.id],
                    query_kwargs={
                        STATUS_QUERY: query_params[index].value
                    })
                response = self.client.patch(url)
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def verify_opinion_content(
                self, opinion: Opinion, response: HttpResponse,
                is_readonly: bool = False, is_preview: bool = False
            ):
        """
        Verify opinion page content for user
        :param opinion: expected opinion
        :param response: opinion response
        :param is_readonly: is readonly flag; default False
        :param is_preview: is preview flag; default False
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check tag for title
        inputs = soup.find_all(id='id_title')
        self.assertEqual(len(inputs), 1)
        title = inputs[0].text if is_readonly else inputs[0].get('value')
        self.assertTrue(title, opinion.title)

        if is_readonly:
            # check for readonly_content div, can't check content as its
            # replaced by javascript
            SoupMixin.find_tag(self, soup.find_all(id='readonly_content'),
                               lambda tag: True)
        else:
            # check textarea tags for content
            SoupMixin.find_tag(self, soup.find_all('textarea'),
                               lambda tag: opinion.content in tag.text)

        # check categories
        if is_readonly:
            CategoryMixin.check_categories(
                self, soup,
                lambda tag: tag.name == 'span'
                and SoupMixin.in_tag_attr(tag, 'class', 'badge'),
                lambda category, tag: category.name == tag.text,
                opinion.categories.all())
        else:
            CategoryMixin.check_category_options(
                self, soup, opinion.categories.all())

        # check fieldset is disabled in read only mode
        if is_readonly:
            pass    # no fieldset in view mode
        else:
            SoupMixin.check_tag(self, soup.find_all('fieldset'), is_readonly,
                                lambda tag: tag.has_attr('disabled'))

        # check status only displayed if not read only,
        # i.e. current user's opinion
        found = False
        for span in soup.find_all('span'):
            if SoupMixin.in_tag_attr(span, 'class', 'badge'):
                found = opinion.status.name == span.text
                if found:
                    break
        if is_readonly:
            self.assertFalse(found)
        else:
            self.assertTrue(found)

        # check preview banner only displayed if opinion is preview status
        if is_preview and opinion.status.name == STATUS_PREVIEW:
            alerts = soup.find_all(attrs={'class': re.compile("alert")})
            self.assertGreaterEqual(len(alerts), 1)
            for alert in alerts:
                SoupMixin.find_tag(self, alert.descendants,
                                   lambda tag: STATUS_PREVIEW in tag.text)

        # check submit button only displayed in not read only mode
        tags = soup.find_all(check_submit_button)
        if is_readonly:
            self.assertEqual(len(tags), 0)
        else:
            self.assertEqual(len(tags), 3)
