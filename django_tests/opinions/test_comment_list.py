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

from bs4 import BeautifulSoup
from django.http import HttpResponse

from opinions.constants import (
    COMMENTS_ROUTE_NAME, ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY,
)
from opinions.models import Opinion, Comment
from opinions.views_utils import CommentSortOrder, PerPage
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_opinion_test_cls import BaseOpinionTest
from .test_comment_view import TestCommentView
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test_cls import BaseUserTest

COMMENT_LIST_TEMPLATE = f'{OPINIONS_APP_NAME}/comment_list.html'
COMMENT_LIST_CONTENT_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/comment_list_content.html'


class TestCommentList(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test comment page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestCommentList, TestCommentList).setUpTestData()

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
            self, order: CommentSortOrder = None, page: int = None,
            per_page: PerPage = None) -> HttpResponse:
        """
        Get the comment page
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
        if page:
            query_kwargs[PAGE_QUERY] = page
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, COMMENTS_ROUTE_NAME),
                query_kwargs=query_kwargs))

    def test_not_logged_in_access(self):
        """ Test must be logged in to access opinion list """
        response = self.get_comment_list_by()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_comment_list(self):
        """ Test page content for comment list """
        opinion = TestCommentList.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        response = self.get_comment_list_by()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, COMMENT_LIST_TEMPLATE)
        self.assertTemplateUsed(response, COMMENT_LIST_CONTENT_TEMPLATE)

    def test_get_comment_list_sorted(self):
        """
        Test page content for sorted comment list
        (doesn't get whole page just, comments)
        """
        comment = TestCommentList.comments[0]
        user = self.login_user_by_id(comment.user.id)

        for order in list(CommentSortOrder):
            # check contents of first page
            expected = TestCommentList.get_expected(
                order, PerPage.DEFAULT)

            with self.subTest(f'order {order}'):
                response = self.get_comment_list_by(order=order)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(
                    response, COMMENT_LIST_CONTENT_TEMPLATE)
                verify_comment_list_content(
                    self, expected, response, msg=order)

    @staticmethod
    def get_expected(order: CommentSortOrder,
                     per_page: [PerPage, None],
                     page_num: int = 0) -> list[Comment]:
        """
        Generate the expected results list
        :param order: sort order of results
        :param per_page: results per page; None will return all
        :param page_num: 0-based number of page to get
        """
        # all published opinions
        expected = TestCommentList.published_comments()
        return sort_expected(
            expected, order, per_page, page_num=page_num)

    def test_get_comment_list_pagination(self):
        """
        Test page content for comment list pagination
        (doesn't get whole page just, opinions)
        """
        opinion = TestCommentList.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        total = len(
            # all published opinions
            TestCommentList.published_comments()
        )

        for per_page in list(PerPage):
            num_pages = int((total + per_page.arg - 1) / per_page.arg)
            for count in range(1, num_pages + 1):

                expected = TestCommentList.get_expected(
                    CommentSortOrder.DEFAULT, per_page, count - 1)

                msg = f'page {count}/{num_pages}'
                with self.subTest(msg):
                    response = self.get_comment_list_by(
                        per_page=per_page, page=count)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(
                        response, COMMENT_LIST_CONTENT_TEMPLATE)
                    verify_comment_list_content(
                        self, expected, response,
                        pagination=num_pages > 1, msg=msg)


def verify_comment_list_content(
            test_case: BaseOpinionTest, expected: list[Comment],
            response: HttpResponse, pagination: bool = False,
            msg: str = ''
        ):
    """
    Verify comment list page content
    :param test_case: opinion test object
    :param expected: expected opinions
    :param response: opinion response
    :param pagination: check for pagination flag
    :param msg: message
    """
    test_case.assertEqual(response.status_code, HTTPStatus.OK)

    soup = BeautifulSoup(
        response.content.decode("utf-8", errors="ignore"), features="lxml"
    )

    # check number of cards
    tags = soup.find_all(
        lambda tag: tag.name == 'div'
        and SoupMixin.in_tag_attr(tag, 'class', 'card')
    )
    test_case.assertEqual(
        len(expected), len(tags),
        f'{msg}: expected {len(expected)} cards, got {len(tags)}')

    for index, comment in enumerate(expected):
        sub_msg = f'{msg} index {index} comment "{comment.content}"'
        with test_case.subTest(sub_msg):

            TestCommentView.verify_comment_content(
                test_case, comment.opinion, comment, response
            )

    if pagination:
        SoupMixin.find_tag(
            test_case, soup.find_all('ul'),
            lambda tag:
            SoupMixin.in_tag_attr(tag, 'class', 'pagination'))

        SoupMixin.find_tag(
            test_case, soup.find_all('li'),
            lambda tag:
            SoupMixin.equal_tag_attr(tag, 'id', 'current-page'))


def sort_expected(expected: list[Comment], order: CommentSortOrder,
                  per_page: [PerPage, None], page_num: int = 0
                  ) -> list[Comment]:
    """
    Sort the expected results list
    :param expected: expected results
    :param order: sort order of results
    :param per_page: results per page; None will return all
    :param page_num: 0-based number of page to get
    """
    author_order = 'author' in order.display.lower()
    status_order = 'status' in order.display.lower()
    expected.sort(
        key=lambda op:
        op.user.username.lower() if author_order else
        op.status.name.lower() if status_order else op.published,
        reverse=order.order.startswith('-')
    )
    if order not in [CommentSortOrder.NEWEST, CommentSortOrder.OLDEST]:
        # secondary sort by oldest
        to_sort = expected.copy()
        expected = []
        field = Opinion.USER_FIELD \
            if author_order else Opinion.STATUS_FIELD

        while len(expected) < len(to_sort):
            # sort in chunks of same attrib value
            look_for = getattr(to_sort[len(expected)], field)
            chunk = list(
                filter(
                    lambda op: look_for == getattr(op, field),
                    to_sort)
            )
            chunk.sort(
                key=lambda op: op.published,
                reverse=False
            )
            expected.extend(chunk)

    # contents of requested page
    if per_page is not None:
        start = per_page.arg * page_num
        expected = expected[start:start + per_page.arg]
    return expected
