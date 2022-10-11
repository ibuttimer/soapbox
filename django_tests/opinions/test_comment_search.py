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
from datetime import datetime, date
from http import HTTPStatus
from typing import Any
from unittest import skip
from zoneinfo import ZoneInfo

from django.http import HttpResponse

from categories.models import Status
from opinions.constants import (
    COMMENT_SEARCH_ROUTE_NAME, ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY,
    CONTENT_QUERY, AUTHOR_QUERY, SEARCH_QUERY,
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY, STATUS_QUERY
)
from opinions.models import Comment
from opinions.views_opinion_list import DATE_QUERIES
from opinions.views_utils import CommentSortOrder, PerPage, QueryStatus

from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_opinion_test_cls import BaseOpinionTest
from .test_comment_list import (
    COMMENT_LIST_TEMPLATE, COMMENT_LIST_CONTENT_TEMPLATE,
    verify_comment_list_content, sort_expected
)
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test_cls import BaseUserTest

DATE_SPACED_FMT = "%d %m %Y"
DATE_SLASHED_FMT = "%d/%m/%Y"
DATE_DASHED_FMT = "%d-%m-%Y"
DATE_DOTTED_FMT = "%d.%m.%Y"


class TestCommentSearch(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test comment page search view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestCommentSearch, TestCommentSearch).setUpTestData()

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

    def get_comment_list_by(
            self, query: dict,
            order: CommentSortOrder = None, page: int = None,
            per_page: PerPage = None) -> HttpResponse:
        """
        Get the comment page
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
                namespaced_url(OPINIONS_APP_NAME, COMMENT_SEARCH_ROUTE_NAME),
                query_kwargs=query_kwargs))

    def test_not_logged_in_access(self):
        """ Test must be logged in to access comment search """
        response = self.get_comment_list_by({})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_comment_list(self):
        """ Test page content for comment list """
        comment = TestCommentSearch.opinions[0]
        user = self.login_user_by_id(comment.user.id)

        response = self.get_comment_list_by({
            CONTENT_QUERY: 'Comment from'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, COMMENT_LIST_TEMPLATE)
        self.assertTemplateUsed(response, COMMENT_LIST_CONTENT_TEMPLATE)

    def test_no_comments_found(self):
        """ Test response for no comments found """
        comment = TestCommentSearch.opinions[0]
        user = self.login_user_by_id(comment.user.id)

        content = 'there are no comments like this'
        for comment in self.comments:
            self.assertNotIn(content, comment.content)

        response = self.get_comment_list_by({
            CONTENT_QUERY: content
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, COMMENT_LIST_TEMPLATE)
        verify_comment_list_content(self, [], response, msg='no content')

    def get_query_options(self) -> tuple[
            Comment, Any, list[tuple[str, str] | tuple[str, Any]]]:
        """
        Get a list of queries
        """
        comment = TestCommentSearch.comments[0]

        # all published comments
        published = TestCommentSearch.published_comments()

        min_date = min(map(lambda op: op.created, published))
        max_date = max(map(lambda op: op.created, published))
        test_date = min_date + ((max_date - min_date) / 2)

        return comment, comment.user, [
            (CONTENT_QUERY, middle_word(comment.content)),
            (AUTHOR_QUERY, comment.user.username[
                           :int(len(comment.user.username)/2)]),
            (STATUS_QUERY, QueryStatus.ALL.arg),
            (STATUS_QUERY, QueryStatus.PUBLISH.arg),
            (ON_OR_AFTER_QUERY, test_date.strftime(DATE_SPACED_FMT)),
            (ON_OR_BEFORE_QUERY, test_date.strftime(DATE_SLASHED_FMT)),
            (AFTER_QUERY, test_date.strftime(DATE_DASHED_FMT)),
            (BEFORE_QUERY, test_date.strftime(DATE_DOTTED_FMT)),
            (EQUAL_QUERY, test_date.strftime(DATE_DOTTED_FMT)),
        ]

    def test_comment_search_sorted(self):
        """
        Test page content for sorted comment search
        (doesn't get whole page just, comments)
        """
        comment, user, queries = self.get_query_options()
        user = self.login_user_by_id(user.id)

        for q, v in queries:
            for order in list(CommentSortOrder):
                # check contents of first page
                query = {
                    q: v
                }
                expected = self.get_expected(
                    query, order, PerPage.DEFAULT)

                msg = f'{q}: {v}, order {order}'
                with self.subTest(msg):
                    response = self.get_comment_list_by(query, order=order)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(
                        response, COMMENT_LIST_CONTENT_TEMPLATE)
                    verify_comment_list_content(
                        self, expected, response, msg=msg)

    def test_search_comment_pagination(self):
        """
        Test page content for comment search pagination
        (doesn't get whole page just, comments)
        """
        opinion, user, queries = self.get_query_options()
        user = self.login_user_by_id(user.id)

        for q, v in queries:
            query = {
                q: v
            }
            expected = self.get_expected(
                query, CommentSortOrder.DEFAULT, None)

            total = len(expected)

            for per_page in list(PerPage):
                num_pages = int((total + per_page.arg - 1) / per_page.arg)
                for count in range(1, num_pages + 1):

                    expected = self.get_expected(
                        query, CommentSortOrder.DEFAULT, per_page, count - 1)

                    msg = f'page {count}/{num_pages} {query}'
                    with self.subTest(msg):
                        response = self.get_comment_list_by(
                            query, per_page=per_page, page=count)
                        self.assertEqual(response.status_code, HTTPStatus.OK)
                        self.assertTemplateUsed(
                            response, COMMENT_LIST_CONTENT_TEMPLATE)
                        verify_comment_list_content(
                            self, expected, response,
                            pagination=num_pages > 1, msg=msg)

    def test_opinion_search_multi_query(self):
        """
        Test page content for multi-query comment search
        (doesn't get whole page just, opinions)
        """
        opinion, user, queries = self.get_query_options()
        user = self.login_user_by_id(user.id)

        for idx1 in range(len(queries)):
            q1, v1 = queries[idx1]
            query = {
                q1: v1
            }

            for idx2 in range(idx1 + 1, len(queries)):
                q2, v2 = queries[idx2]
                query.update({
                    q2: v2
                })

                # check contents of first page
                expected = self.get_expected(
                    query, CommentSortOrder.DEFAULT, PerPage.DEFAULT)

                msg = f'{query}'
                with self.subTest(msg):
                    response = self.get_comment_list_by(query)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(
                        response, COMMENT_LIST_CONTENT_TEMPLATE)
                    verify_comment_list_content(
                        self, expected, response, msg=msg)

    def get_expected(self, query: dict, order: CommentSortOrder,
                     per_page: [PerPage, None], page_num: int = 0
                     ) -> list[Comment]:
        """
        Generate the expected results list
        :param query: query parameters
        :param order: sort order of results
        :param per_page: results per page; None will return all
        :param page_num: 0-based number of page to get
        """
        # all published comments
        expected = TestCommentSearch.published_comments()

        for k, v in query.items():
            if v is None:
                continue
            filter_func = None
            if k in [CONTENT_QUERY]:
                filter_func = text_in_field(Comment.CONTENT_FIELD, v)
            elif k == AUTHOR_QUERY:
                filter_func = text_in_field([
                    Comment.USER_FIELD,
                    User.USERNAME_FIELD
                ], v)
            elif k == STATUS_QUERY:
                if v != QueryStatus.ALL.arg:
                    query_status = \
                        list(filter(lambda qs: qs.arg == v, QueryStatus))
                    self.assertEqual(len(query_status), 1,
                                     f'QueryStatus {v} not found')

                    filter_func = text_in_field([
                        Comment.STATUS_FIELD,
                        Status.NAME_FIELD
                    ], query_status[0].display)
                # else all statuses so no need for filtering
            elif k in DATE_QUERIES:
                filter_func = date_check(v, k)

            expected = list(
                filter(
                    filter_func, expected
                ))
            if len(expected) == 0:
                break   # skip unnecessary additional filtering

        return sort_expected(
            expected, order, per_page, page_num=page_num)


def text_in_field(field: [str, list[str]], text: str):
    """
    Check for `text` in the specified field
    :param field: field(s) to check
    :param text: text to look for
    :return: filter function
    """
    fields = [field] if isinstance(field, str) else field

    def func(instance):
        obj = instance
        for fld in fields[:-1]:
            obj = getattr(obj, fld)
        return text in getattr(obj, fields[-1])

    return func


def date_check(date_str: str, test: str):
    """
    Check opinion date satisfies condition
    :param date_str: date
    :param test: test for date
    :return: filter function
    """
    fmt = DATE_SPACED_FMT if ' ' in date_str else \
        DATE_SLASHED_FMT if '/' in date_str else \
        DATE_DASHED_FMT if '-' in date_str else DATE_DOTTED_FMT
    test_date = datetime.strptime(date_str, fmt)
    test_date = test_date.replace(tzinfo=ZoneInfo("UTC"))
    test_date = date(test_date.year, test_date.month, test_date.day)

    def func(op):
        op_date = date(op.created.year, op.created.month, op.created.day)
        return op_date >= test_date if test == ON_OR_AFTER_QUERY else \
            op_date <= test_date if test == ON_OR_BEFORE_QUERY else \
            op_date > test_date if test == AFTER_QUERY else \
            op_date < test_date if test == BEFORE_QUERY else \
            op_date == test_date    # EQUAL_QUERY

    return func


def middle_word(text: str):
    """
    Get middle word in text
    :param text:
    :return:
    """
    split = text.split()
    return split[int(len(split) / 2)]
