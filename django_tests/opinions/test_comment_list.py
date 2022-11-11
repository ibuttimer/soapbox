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
from opinions.models import Comment
from opinions.enums import CommentSortOrder, PerPage
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_comment_test import BaseCommentTest
from .base_opinion_test import BaseOpinionTest
from .test_comment_view import TestCommentView
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test import BaseUserTest

COMMENT_LIST_TEMPLATE = f'{OPINIONS_APP_NAME}/comment_list.html'
COMMENT_LIST_CONTENT_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/comment_list_content.html'
COMMENT_TEMPLATE = f'{OPINIONS_APP_NAME}/snippet/comment.html'


class TestCommentList(SoupMixin, CategoryMixin, BaseCommentTest):
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
        self.assert_comment_list_templates(response)

    def assert_comment_list_templates(self, response: HttpResponse):
        """ Check the templates used in response """
        self.assertTemplateUsed(response, COMMENT_LIST_TEMPLATE)
        self.assertTemplateUsed(response, COMMENT_LIST_CONTENT_TEMPLATE)
        self.assertTemplateUsed(response, COMMENT_TEMPLATE)

    def test_get_comment_list_sorted(self):
        """
        Test page content for sorted comment list
        (doesn't get whole page just, comments)
        """
        comment = TestCommentList.comments[0]
        user = self.login_user_by_id(comment.user.id)

        for order in list(CommentSortOrder):
            # check contents of first page
            msg = f'order {order}'
            expected = self.get_expected_list(
                order, user, per_page=PerPage.DEFAULT)

            with self.subTest(msg):
                response = self.get_comment_list_by(order=order)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assert_comment_list_templates(response)
                verify_comment_list_content(
                    self, expected, response, user=user, msg=order)

    def get_expected_list(self, order: CommentSortOrder, user: User,
                          per_page: [PerPage, None] = None,
                          page_num: int = 0) -> list[Comment]:
        """
        Generate the expected results list
        :param order: sort order of results
        :param user: current user
        :param per_page: results per page; None will return all
        :param page_num: 0-based number of page to get
        """
        return BaseCommentTest.get_expected(
            self, {
                # no query required as default is all published comments
            }, order, user, per_page=per_page, page_num=page_num)

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

                msg = f'page {count}/{num_pages}'
                expected = self.get_expected_list(
                    CommentSortOrder.DEFAULT, user,
                    per_page=per_page, page_num=count - 1)

                with self.subTest(msg):
                    response = self.get_comment_list_by(
                        per_page=per_page, page=count)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assert_comment_list_templates(response)
                    verify_comment_list_content(
                        self, expected, response, user=user,
                        pagination=num_pages > 1, msg=msg)


def verify_comment_list_content(
        test_case: BaseOpinionTest, expected: list[Comment],
        response: HttpResponse, user: User = None, pagination: bool = False,
        msg: str = ''):
    """
    Verify comment list page content
    :param test_case: opinion test object
    :param expected: expected comments
    :param response: comments response
    :param user: current user; default None
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
        f'{msg}: expected {len(expected)} card(s), got {len(tags)}')

    for index, comment in enumerate(expected):
        sub_msg = f'{msg} | index {index} comment "{comment.content}"'
        with test_case.subTest(sub_msg):
            TestCommentView.verify_comment_content(
                test_case, comment, response, user=user)

    if pagination:
        SoupMixin.find_tag(
            test_case, soup.find_all('ul'),
            lambda tag:
            SoupMixin.in_tag_attr(tag, 'class', 'pagination'))

        SoupMixin.find_tag(
            test_case, soup.find_all('li'),
            lambda tag:
            SoupMixin.equal_tag_attr(tag, 'id', 'current-page'))
