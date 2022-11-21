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
from unittest import skip

from django.http import HttpResponse

from opinions.constants import (
    ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, OPINION_IN_REVIEW_ROUTE_NAME,
    REVIEW_QUERY
)
from opinions.models import Opinion
from opinions.enums import OpinionSortOrder, PerPage, QueryStatus
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_opinion_test import BaseOpinionTest
from .test_opinion_list import OPINION_LIST_TEMPLATE, \
    verify_opinion_list_content, OPINION_LIST_SORT_TEMPLATE
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test import BaseUserTest


class TestOpinionReviewList(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test opinion review list page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionReviewList, cls).setUpTestData()

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

    def get_opinion_review_list_by(
            self, status: QueryStatus = QueryStatus.PENDING_REVIEW,
            order: OpinionSortOrder = None, page: int = None,
            per_page: PerPage = None) -> HttpResponse:
        """
        Get the opinion review list
        :param status: review status
        :param order:
            order to retrieve opinions in; default None i.e. don't care
        :param page: 1-based page number to get
        :param per_page: options per page
        """
        query_kwargs = {
            k: v.arg for k, v in [
                (ORDER_QUERY, order),
                (PER_PAGE_QUERY, per_page),
            ] if v is not None
        }
        query_kwargs[REVIEW_QUERY] = status.arg
        if page:
            query_kwargs[PAGE_QUERY] = page
        return self.client.get(
            reverse_q(
                namespaced_url(
                    OPINIONS_APP_NAME, OPINION_IN_REVIEW_ROUTE_NAME),
                query_kwargs=query_kwargs))

    def test_not_logged_in_access(self):
        """ Test must be logged in to access opinion review list """
        response = self.get_opinion_review_list_by()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_opinion_review_list(self):
        """ Test page template for opinion review list """
        opinion = TestOpinionReviewList.opinions[0]
        user = self.get_other_user(opinion.user, moderator=True)
        self.login_user_by_id(user.id)

        response = self.get_opinion_review_list_by(
            status=QueryStatus.PENDING_REVIEW)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_LIST_TEMPLATE)

    def test_not_moderator_opinion_review_list(self):
        """
        Test page content for non-moderator
        (doesn't get whole page just, opinions)
        """
        opinion = TestOpinionReviewList.opinions[0]
        user = self.get_other_user(opinion.user)
        self.login_user_by_id(user.id)

        # check contents of first page
        for status in [
            QueryStatus.PENDING_REVIEW, QueryStatus.UNDER_REVIEW,
            QueryStatus.APPROVED
        ]:
            msg = f'{status.display}'

            expected = self.get_expected_list(
                status, OpinionSortOrder.DEFAULT, user,
                per_page=PerPage.DEFAULT)

            with self.subTest(msg):
                response = self.get_opinion_review_list_by(
                    status=status, order=OpinionSortOrder.DEFAULT)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response,
                                        OPINION_LIST_SORT_TEMPLATE)
                verify_opinion_list_content(
                    self, expected, response, user=user, msg=msg)

    def test_get_opinion_review_list_sorted(self):
        """
        Test page content for sorted opinion list
        (doesn't get whole page just, opinions)
        """
        opinion = TestOpinionReviewList.opinions[0]
        user = self.get_other_user(opinion.user, moderator=True)
        self.login_user_by_id(user.id)

        for order in list(OpinionSortOrder):
            # check contents of first page
            for status in [
                QueryStatus.PENDING_REVIEW, QueryStatus.UNDER_REVIEW,
                QueryStatus.APPROVED
            ]:
                msg = f'{status.display}/{order}'

                expected = self.get_expected_list(
                    status, order, user, per_page=PerPage.DEFAULT)

                with self.subTest(msg):
                    response = self.get_opinion_review_list_by(
                        status=status, order=order)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(response,
                                            OPINION_LIST_SORT_TEMPLATE)
                    verify_opinion_list_content(
                        self, expected, response, user=user, msg=order)

    def get_expected_list(self, status: QueryStatus,
                          order: OpinionSortOrder, user: User,
                          per_page: [PerPage, None] = None,
                          page_num: int = 0) -> list[Opinion]:
        """
        Generate the expected results list
        :param status: required status
        :param order: sort order of results
        :param user: current user
        :param per_page: results per page; None will return all
        :param page_num: 0-based number of page to get
        """
        return BaseOpinionTest.get_expected(
            self, {
                REVIEW_QUERY: status.display
            }, order, user, per_page=per_page, page_num=page_num)
