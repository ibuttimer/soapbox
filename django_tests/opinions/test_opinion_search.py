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
from typing import Any
from unittest import skip

from django.http import HttpResponse

from opinions.constants import (
    OPINION_SEARCH_ROUTE_NAME, ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY,
    TITLE_QUERY, CONTENT_QUERY, AUTHOR_QUERY, CATEGORY_QUERY, SEARCH_QUERY,
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY, STATUS_QUERY, HIDDEN_QUERY
)
from opinions.models import Opinion
from opinions.enums import QueryStatus, OpinionSortOrder, PerPage, Hidden
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_opinion_test import (
    BaseOpinionTest, middle_word,
    DATE_SPACED_FMT, DATE_SLASHED_FMT, DATE_DASHED_FMT, DATE_DOTTED_FMT
)
from .test_opinion_list import (
    OPINION_LIST_TEMPLATE, OPINION_LIST_SORT_TEMPLATE,
    verify_opinion_list_content
)
from ..category_mixin_test import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test import BaseUserTest


class TestOpinionSearch(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionSearch, cls).setUpTestData()

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

    def get_opinion_list_by(
            self, query: dict,
            order: OpinionSortOrder = None, page: int = None,
            per_page: PerPage = None) -> HttpResponse:
        """
        Get the opinion page
        :param query: query parameters
        :param order:
            order to retrieve opinions in; default None i.e. don't care
        :param page: 1-based page number to get
        :param per_page: options per page
        """
        # Note: values must be in quotes for search query and joined by '+'
        #       to simulate coming from navbar search form
        query_kwargs = {
            SEARCH_QUERY: '+'.join([
                    f'{k}="{v}"' for k, v in query.items() if v is not None
                ])
        }
        query_kwargs.update({
            k: v.arg for k, v in [
                (ORDER_QUERY, order),
                (PER_PAGE_QUERY, per_page),
            ] if v is not None
        })
        if page:
            query_kwargs[PAGE_QUERY] = page
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, OPINION_SEARCH_ROUTE_NAME),
                query_kwargs=query_kwargs))

    def test_not_logged_in_access(self):
        """ Test must be logged in to access opinion search """
        response = self.get_opinion_list_by({})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_opinion_list(self):
        """ Test page content for opinion list """
        opinion = TestOpinionSearch.opinions[0]
        _ = self.login_user_by_id(opinion.user.id)

        response = self.get_opinion_list_by({
            TITLE_QUERY: 'informative'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_LIST_TEMPLATE)

    def test_no_opinions_found(self):
        """ Test response for no opinions found """
        opinion = TestOpinionSearch.opinions[0]
        _ = self.login_user_by_id(opinion.user.id)

        title = 'there are no titles like this'
        for opinion in self.opinions:
            self.assertNotEqual(title, opinion.title)

        response = self.get_opinion_list_by({
            TITLE_QUERY: title
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_LIST_TEMPLATE)
        verify_opinion_list_content(self, [], response, msg='no content')

    def get_query_options(self) -> tuple[Opinion, User, list[str, Any]]:
        """
        Get a list of queries
        :return: tuple of opinion, opinion author and query options
        """
        opinion = TestOpinionSearch.opinions[0]

        # all published opinions (both hidden and unhidden)
        published = TestOpinionSearch.published_opinions()

        min_date = min(map(lambda op: op.published, published))
        max_date = max(map(lambda op: op.published, published))
        test_date = min_date + ((max_date - min_date) / 2)

        return opinion, opinion.user, [
            (TITLE_QUERY, middle_word(opinion.title)),
            (CONTENT_QUERY, middle_word(opinion.content)),
            (AUTHOR_QUERY, opinion.user.username[
                           :int(len(opinion.user.username)/2)]),
            (CATEGORY_QUERY, opinion.categories.all()[
                int(opinion.categories.count()/2)].name),
            # TODO partial category name test
            # (CATEGORY_QUERY, opinion.categories.all()[
            #     int(opinion.categories.count()/2)].name[:2]),
            (STATUS_QUERY, QueryStatus.ALL.arg),
            (STATUS_QUERY, QueryStatus.PUBLISH.arg),
            (STATUS_QUERY, QueryStatus.PUBLISH.arg[
                           :int(len(QueryStatus.PUBLISH.arg) / 2)]),
            (HIDDEN_QUERY, Hidden.YES.arg),
            (HIDDEN_QUERY, Hidden.NO.arg),
            (HIDDEN_QUERY, Hidden.IGNORE.arg),
            (ON_OR_AFTER_QUERY, test_date.strftime(DATE_SPACED_FMT)),
            (ON_OR_BEFORE_QUERY, test_date.strftime(DATE_SLASHED_FMT)),
            (AFTER_QUERY, test_date.strftime(DATE_DASHED_FMT)),
            (BEFORE_QUERY, test_date.strftime(DATE_DOTTED_FMT)),
            (EQUAL_QUERY, test_date.strftime(DATE_DOTTED_FMT)),
        ]

    def test_opinion_search_sorted(self):
        """
        Test page content for sorted opinion search
        (doesn't get whole page just, opinions)
        """
        opinion, user, queries = self.get_query_options()
        user = self.login_user_by_id(user.id)

        for qry, val in queries:
            for order in list(OpinionSortOrder):
                # check contents of first page
                query = {
                    qry: val
                }

                msg = f'{qry}: {val}, order {order}'
                expected = BaseOpinionTest.get_expected(
                    self, query, order, user, per_page=PerPage.DEFAULT)
                msg = f'{msg}\n{expected}\n'

                with self.subTest(msg):
                    response = self.get_opinion_list_by(query, order=order)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(
                        response, OPINION_LIST_SORT_TEMPLATE)
                    verify_opinion_list_content(
                        self, expected, response, user=user, msg=msg)

    def test_search_opinion_pagination(self):
        """
        Test page content for opinion search pagination
        (doesn't get whole page just, opinions)
        """
        opinion, user, queries = self.get_query_options()
        user = self.login_user_by_id(user.id)

        for qry, val in queries:
            query = {
                qry: val
            }
            expected = BaseOpinionTest.get_expected(
                self, query, OpinionSortOrder.DEFAULT, user)

            total = len(expected)

            for per_page in list(PerPage):
                num_pages = int((total + per_page.arg - 1) / per_page.arg)
                for count in range(1, num_pages + 1):
                    msg = f'{query}  page {count}/{num_pages}'

                    expected = BaseOpinionTest.get_expected(
                        self, query, OpinionSortOrder.DEFAULT, user,
                        per_page=per_page, page_num=count - 1)

                    with self.subTest(msg):
                        response = self.get_opinion_list_by(
                            query, per_page=per_page, page=count)
                        self.assertEqual(response.status_code, HTTPStatus.OK)
                        self.assertTemplateUsed(
                            response, OPINION_LIST_SORT_TEMPLATE)
                        verify_opinion_list_content(
                            self, expected, response, user=user,
                            pagination=num_pages > 1, msg=msg)

    def test_opinion_search_multi_query(self):
        """
        Test page content for multi-query opinion search
        (doesn't get whole page just, opinions)
        """
        opinion, user, queries = self.get_query_options()
        user = self.login_user_by_id(user.id)

        for idx1 in range(len(queries)):
            qry1, val1 = queries[idx1]
            query = {
                qry1: val1
            }

            for idx2 in range(idx1 + 1, len(queries)):
                qry2, val2 = queries[idx2]
                query.update({
                    qry2: val2
                })

                msg = f'{query}'
                # check contents of first page
                expected = BaseOpinionTest.get_expected(
                    self, query, OpinionSortOrder.DEFAULT,
                    user, per_page=PerPage.DEFAULT)

                with self.subTest(msg):
                    response = self.get_opinion_list_by(query)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(
                        response, OPINION_LIST_SORT_TEMPLATE)
                    verify_opinion_list_content(
                        self, expected, response, user=user, msg=msg)
