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
from typing import Optional, Callable, Any

from bs4 import BeautifulSoup, Tag
from django.http import HttpResponse
from django.test import TestCase

from categories import (
    STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED
)
from categories.models import Status
from opinions import OPINION_STATUS_ID_ROUTE_NAME
from opinions.constants import (
    STATUS_QUERY, UNDER_REVIEW_TITLE, UNDER_REVIEW_OPINION_CONTENT
)
from opinions.models import Opinion
from opinions.enums import QueryStatus, ViewMode
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_opinion_test import BaseOpinionTest
from .opinion_mixin_test import OpinionMixin, AccessBy
from .test_opinion_create import is_submit_button, OPINION_FORM_TEMPLATE
from ..category_mixin_test import CategoryMixin
from ..soup_mixin import SoupMixin, MatchTest

OPINION_VIEW_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_view.html'

# query params to match BaseOpinionTest.STATUSES
QUERY_PARAMS = {
    STATUS_DRAFT: QueryStatus.DRAFT,
    STATUS_PREVIEW: QueryStatus.PREVIEW,
    STATUS_PUBLISHED: QueryStatus.PUBLISH,
}


class TestOpinionView(
        SoupMixin, CategoryMixin, OpinionMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionView, cls).setUpTestData()

    def test_not_logged_in_access_by_id(self):
        """ Test must be logged in to access opinion by id """
        response = self.get_opinion_by_id(TestOpinionView.opinions[0].id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_logged_in_access_by_slug(self):
        """ Test must be logged in to access opinion by slug """
        response = self.get_opinion_by_slug(TestOpinionView.opinions[0].slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def check_get_own_opinion(self, opinion_by: AccessBy):
        """
        Test access to own opinions
        :param opinion_by: method of accessing opinion; one of AccessBy
        """
        opinion = TestOpinionView.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        for status in [STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED]:
            for mode in ViewMode:
                msg = f'{opinion_by} - status {status} - mode {mode}'
                with self.subTest(msg):
                    # get list of own opinions
                    opinions = self.get_own_opinions(user, status)
                    opinion = opinions[0]

                    response = self.get_opinion_by(
                        opinion_by.identifier(opinion), opinion_by, mode=mode)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assert_template(response, mode)
                    TestOpinionView.verify_opinion_content(
                        self, opinion, response, user=user, mode=mode)

    def assert_template(
            self, response: Any = None, mode: ViewMode = ViewMode.DEFAULT,
            msg_prefix: str = "", count: Any = None):
        """ Check the template used """
        self.assertTemplateUsed(
            response=response, template_name=OPINION_FORM_TEMPLATE
            if mode == ViewMode.EDIT else OPINION_VIEW_TEMPLATE,
            msg_prefix=msg_prefix, count=count)

    def test_get_own_opinion_by_id(self):
        """ Test page content for opinion by id of logged-in user """
        self.check_get_own_opinion(AccessBy.BY_ID)

    def test_get_own_opinion_by_slug(self):
        """ Test page content for opinion by slug of logged-in user """
        self.check_get_own_opinion(AccessBy.BY_SLUG)

    def get_own_opinions(
            self, user: User, status: str) -> list[Opinion]:
        """
        Get a list of users' opinions with the specified status
        :param user: user to
        :param status: required status
        :return: list of opinions
        """
        # get list of users' published opinions
        opinions = list(
            filter(lambda op: op.user.id == user.id
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

    def check_get_other_opinion(
        self, opinion_by: AccessBy, find_func: Optional[Callable] = None,
        mode: ViewMode = ViewMode.READ_ONLY
    ):
        """ Test page content for opinion of not logged-in user """
        _, key = TestOpinionView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        # get list of other users' published opinions
        opinions = self.get_other_users_opinions(
            logged_in_user, STATUS_PUBLISHED)
        opinion = opinions[0] if find_func is None else find_func(opinions)

        self.assertNotEqual(logged_in_user, opinion.user)
        response = self.get_opinion_by(
            opinion_by.identifier(opinion), opinion_by)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assert_template(response, ViewMode.READ_ONLY)
        TestOpinionView.verify_opinion_content(
            self, opinion, response, user=logged_in_user, mode=mode)

    def test_get_other_opinion_by_id(self):
        """ Test page content for opinion by id of not logged-in user """
        self.check_get_other_opinion(AccessBy.BY_ID)

    def test_get_other_opinion_by_slug(self):
        """ Test page content for opinion by slug of not logged-in user """
        self.check_get_other_opinion(AccessBy.BY_SLUG)

    def test_get_under_review_opinion_by_id(self):
        """
        Test page content for under review opinion by id of not logged-in user
        """
        def find_func(opinions):
            return self.find_under_review(opinions)[0]
        self.check_get_other_opinion(AccessBy.BY_ID, find_func=find_func)

    def test_get_under_review_opinion_by_slug(self):
        """
        Test page content for under review opinion by slug of not logged-in
        user
        """
        def find_func(opinions):
            return self.find_under_review(opinions)[0]
        self.check_get_other_opinion(AccessBy.BY_SLUG, find_func=find_func)

    def find_under_review(self, opinions: list[Opinion]) -> list[Opinion]:
        ids = list(
            map(lambda op: op.id, TestOpinionView.reported_opinions)
        )
        return list(filter(lambda op: op.id in ids, opinions))

    def check_other_opinion_access(self, opinion_by: AccessBy,
                                   mode: ViewMode = ViewMode.READ_ONLY):
        """
        Test access to unpublished opinions of not logged-in user
        :param opinion_by: method of accessing opinion; one of AccessBy
        :param mode: view mode: default ViewMode.READ_ONLY
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
                response = self.get_opinion_by(
                    opinion_by.identifier(opinion), opinion_by,
                    mode=mode)
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_other_wip_opinion_access_by_id(self):
        """
        Test access to unpublished opinions by id of not logged-in user
        """
        for mode in ViewMode:
            self.check_other_opinion_access(AccessBy.BY_ID, mode=mode)

    def test_get_other_wip_opinion_access_by_slug(self):
        """
        Test access to unpublished opinions by slug of not logged-in user
        """
        for mode in ViewMode:
            self.check_other_opinion_access(AccessBy.BY_SLUG, mode=mode)

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
                self.assert_template(response, ViewMode.PREVIEW)
                TestOpinionView.verify_opinion_content(
                    self, opinion, response, user=logged_in_user,
                    mode=ViewMode.PREVIEW)

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
                    namespaced_url(
                        OPINIONS_APP_NAME, OPINION_STATUS_ID_ROUTE_NAME),
                    args=[opinion.id],
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
                    namespaced_url(
                        OPINIONS_APP_NAME, OPINION_STATUS_ID_ROUTE_NAME),
                    args=[opinion.id],
                    query_kwargs={
                        STATUS_QUERY: query_params[index].value
                    })
                response = self.client.patch(url)
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    @staticmethod
    def verify_opinion_content(
            test_case: TestCase, opinion: Opinion, response: HttpResponse,
            user: User = None, mode: ViewMode = ViewMode.DEFAULT):
        """
        Verify opinion page content for user
        :param test_case: TestCase instance
        :param opinion: expected opinion
        :param response: opinion response
        :param user: current user; default None
        :param mode: one of ViewMode; default ViewMode.DEFAULT
        """
        is_readonly = mode.is_non_edit_mode
        is_preview = mode == ViewMode.PREVIEW
        is_edit = mode == ViewMode.EDIT

        test_case.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode(
                "utf-8", errors="ignore"), features="lxml"
        )

        under_review = user and opinion.user != user
        if under_review:
            under_review = any(
                map(lambda op: op.id == opinion.id,
                    test_case.reported_opinions)
            )
        if under_review:
            expected_title = UNDER_REVIEW_TITLE
            expected_content = UNDER_REVIEW_OPINION_CONTENT
        else:
            expected_title = opinion.title
            expected_content = opinion.excerpt

        # check tag for title
        # (in edit mode id is the auto id of the form field)
        inputs = soup.find_all(id='id_title' if is_edit else 'id--title')
        test_case.assertEqual(len(inputs), 1)
        title = inputs[0].text.strip() if is_readonly \
            else inputs[0].get('value')
        test_case.assertEqual(title, expected_title)

        if is_readonly:
            # check for readonly_content div
            content = SoupMixin.find_tag(
                test_case, soup.find_all(id='readonly_content'),
                lambda tag: True)
            if under_review:
                test_case.assertEqual(content.text.strip(), expected_content)
            # else can't check content as its replaced by javascript
        else:
            # check textarea tags for content
            SoupMixin.find_tag(test_case, soup.find_all('textarea'),
                               lambda tag: opinion.content in tag.text)

        # check categories
        if is_readonly:
            CategoryMixin.check_categories(
                test_case, soup,
                lambda tag: tag.name == 'span'
                and SoupMixin.in_tag_attr(tag, 'class', 'badge'),
                lambda category, tag: category.name == tag.text,
                opinion.categories.all())
        else:
            CategoryMixin.check_category_options(
                test_case, soup, opinion.categories.all())

        # check fieldset is disabled in read only mode
        if is_readonly:
            pass    # no fieldset in view mode
        else:
            SoupMixin.check_tag(test_case, soup.find_all('fieldset'),
                                is_readonly,
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
            test_case.assertFalse(found)
        else:
            test_case.assertTrue(found)

        # check preview banner only displayed if opinion is preview status
        if is_preview and opinion.status.name == STATUS_PREVIEW:
            alerts = soup.find_all(attrs={'class': re.compile("alert")})
            test_case.assertGreaterEqual(len(alerts), 1)
            for alert in alerts:
                # text will be found repeatably, as using 'descendants'
                SoupMixin.find_tag(test_case, alert.descendants,
                                   lambda tag: STATUS_PREVIEW in tag.text,
                                   match=MatchTest.GT_EQ)

        # check submit buttons only displayed in not read only mode
        tags = soup.find_all(is_submit_button)
        if is_readonly:
            test_case.assertEqual(len(tags), 0)
        else:
            # save draft/preview/publish
            test_case.assertEqual(len(tags), 3)

        # check delete button only displayed in not read only mode
        tags = soup.find_all(is_delete_button)
        if is_readonly:
            test_case.assertEqual(len(tags), 0)
        else:
            test_case.assertEqual(len(tags), 1)


def is_delete_button(tag: Tag):
    """
    Check `tag` is an opinion delete button
    :param tag: tag to check
    :return: True is opinion submit button, otherwise False
    """
    return tag.name == 'button' \
        and SoupMixin.equal_tag_attr(tag, 'type', 'button') \
        and SoupMixin.in_tag_attr(tag, 'class', 'btn__submit-opinion')
