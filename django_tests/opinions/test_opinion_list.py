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
    OPINIONS_ROUTE_NAME, ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY
)
from opinions.models import Opinion
from opinions.views_utils import OpinionSortOrder, OpinionPerPage
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q
from .base_opinion_test_cls import BaseOpinionTest
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test_cls import BaseUserTest

OPINION_LIST_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_list.html'
OPINION_LIST_SORT_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_list_content.html'


class TestOpinionList(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionList, TestOpinionList).setUpTestData()

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
            self, order: OpinionSortOrder = None, page: int = None,
            per_page: OpinionPerPage = None) -> HttpResponse:
        """
        Get the opinion page
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
            reverse_q(OPINIONS_ROUTE_NAME, query_kwargs=query_kwargs))

    def test_not_logged_in_access(self):
        """ Test must be logged in to access opinion list """
        response = self.get_opinion_list_by()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_opinion_list(self):
        """ Test page content for opinion list """
        opinion = TestOpinionList.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        response = self.get_opinion_list_by()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OPINION_LIST_TEMPLATE)

    def test_get_opinion_list_sorted(self):
        """
        Test page content for sorted opinion list
        (doesn't get whole page just, opinions)
        """
        opinion = TestOpinionList.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        for order in list(OpinionSortOrder):
            # check contents of first page
            expected = TestOpinionList.get_expected(
                order, OpinionPerPage.DEFAULT)

            with self.subTest(f'order {order}'):
                response = self.get_opinion_list_by(order=order)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, OPINION_LIST_SORT_TEMPLATE)
                verify_opinion_list_content(
                    self, expected, response, msg=order)

    @staticmethod
    def get_expected(order: OpinionSortOrder,
                     per_page: [OpinionPerPage, None],
                     page_num: int = 0) -> list[Opinion]:
        """
        Generate the expected results list
        :param order: sort order of results
        :param per_page: results per page; None will return all
        :param page_num: 0-based number of page to get
        """
        # all published opinions
        expected = TestOpinionList.published()
        return sort_expected(
            expected, order, per_page, page_num=page_num)

    def test_get_opinion_list_pagination(self):
        """
        Test page content for opinion list pagination
        (doesn't get whole page just, opinions)
        """
        opinion = TestOpinionList.opinions[0]
        user = self.login_user_by_id(opinion.user.id)

        total = len(
            # all published opinions
            TestOpinionList.published()
        )

        for per_page in list(OpinionPerPage):
            num_pages = int((total + per_page.arg - 1) / per_page.arg)
            for count in range(1, num_pages + 1):

                expected = TestOpinionList.get_expected(
                    OpinionSortOrder.DEFAULT, per_page, count - 1)

                msg = f'page {count}/{num_pages}'
                with self.subTest(msg):
                    response = self.get_opinion_list_by(
                        per_page=per_page, page=count)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertTemplateUsed(
                        response, OPINION_LIST_SORT_TEMPLATE)
                    verify_opinion_list_content(
                        self, expected, response,
                        pagination=num_pages > 1, msg=msg)


def verify_opinion_list_content(
            test_case: BaseOpinionTest, expected: list[Opinion],
            response: HttpResponse, pagination: bool = False,
            msg: str = ''
        ):
    """
    Verify opinion list page content
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
    test_case.assertEqual(len(tags), len(expected))

    for index, opinion in enumerate(expected):
        sub_msg = f'{msg} index {index} opinion ' \
                  f'"{opinion.user.username} {opinion.title}"'
        with test_case.subTest(sub_msg):

            # check title
            tags = soup.find_all(id=f'id_title_{index + 1}')
            test_case.assertEqual(len(tags), 1)
            test_case.assertTrue(tags[0].text, opinion.title)

            # check excerpt
            tags = soup.find_all(id=f'excerpt_{index + 1}')
            test_case.assertEqual(len(tags), 1)
            test_case.assertTrue(tags[0].text, opinion.excerpt)

            # check categories
            CategoryMixin.check_categories(
                test_case, soup,
                lambda tag: tag.name == 'span'
                and TestOpinionList.equal_tag_attr(
                    tag.parent, 'id', f'categories_{index + 1}'),
                lambda category, tag: category.name == tag.text,
                opinion.categories.all(),
                msg=sub_msg)

    if pagination:
        SoupMixin.find_tag(
            test_case, soup.find_all('ul'),
            lambda tag:
            SoupMixin.in_tag_attr(tag, 'class', 'pagination'))

        SoupMixin.find_tag(
            test_case, soup.find_all('li'),
            lambda tag:
            SoupMixin.equal_tag_attr(tag, 'id', 'current-page'))


def sort_expected(expected: list[Opinion], order: OpinionSortOrder,
                  per_page: [OpinionPerPage, None], page_num: int = 0
                  ) -> list[Opinion]:
    """
    Sort the expected results list
    :param expected: expected results
    :param order: sort order of results
    :param per_page: results per page; None will return all
    :param page_num: 0-based number of page to get
    """
    title_order = 'title' in order.display.lower()
    author_order = 'author' in order.display.lower()
    expected.sort(
        key=lambda op:
        op.title.lower() if title_order else
        op.user.username.lower() if author_order else op.published,
        reverse=order == OpinionSortOrder.NEWEST or
        order == OpinionSortOrder.TITLE_ZA or
        order == OpinionSortOrder.AUTHOR_ZA
    )
    if order not in [OpinionSortOrder.NEWEST, OpinionSortOrder.OLDEST]:
        # secondary sort by newest
        to_sort = expected.copy()
        expected = []
        field = Opinion.USER_FIELD \
            if author_order else Opinion.TITLE_FIELD

        while len(expected) < len(to_sort):
            look_for = getattr(to_sort[len(expected)], field)
            author_ops = list(
                filter(
                    lambda op: look_for == getattr(op, field),
                    to_sort)
            )
            author_ops.sort(
                key=lambda op: op.published,
                reverse=True
            )
            expected.extend(author_ops)

    # contents of requested page
    if per_page is not None:
        start = per_page.arg * page_num
        expected = expected[start:start + per_page.arg]
    return expected
