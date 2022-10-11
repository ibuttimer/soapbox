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
from django.test import TestCase

from categories import (
    STATUS_PUBLISHED
)
from opinions import (
    OPINION_ID_ROUTE_NAME
)
from opinions.models import Opinion, Comment
from soapbox import OPINIONS_APP_NAME, USER_APP_NAME
from user import USER_ID_ROUTE_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_opinion_test_cls import BaseOpinionTest
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test_cls import BaseUserTest

OPINION_VIEW_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_view.html'
OPINION_VIEW_COMMENTS_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/snippet/view_comments.html'
OPINION_COMMENTS_BUNDLE_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/snippet/comment_bundle.html'
OPINION_COMMENTS_REACTIONS_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/snippet/reactions.html'


class TestCommentView(SoupMixin, CategoryMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestCommentView, TestCommentView).setUpTestData()

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
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
                args=[pk]))

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
                   TestCommentView.opinions)
        )
        self.assertGreaterEqual(
            len(opinions), 1, msg=f'No opinions with {status} status')
        return opinions

    def test_get_other_opinion_with_comment(self):
        """ Test comment content of opinion of not logged-in user """
        _, key = TestCommentView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        # get list of other users' published opinions
        opinions = self.get_other_users_opinions(
            logged_in_user, STATUS_PUBLISHED)
        opinion = opinions[0]

        self.assertNotEqual(logged_in_user, opinion.user)
        response = self.get_opinion_by_id(opinion.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for template in [
            OPINION_VIEW_TEMPLATE, OPINION_VIEW_COMMENTS_TEMPLATE,
            OPINION_COMMENTS_BUNDLE_TEMPLATE,
            OPINION_COMMENTS_REACTIONS_TEMPLATE
        ]:
            self.assertTemplateUsed(response, template)

        comments = Comment.objects.filter(**{
            Comment.OPINION_FIELD: opinion,
            Comment.PARENT_FIELD: Comment.NO_PARENT
        })
        TestCommentView.verify_comment_content(
            self, opinion, comments[0], response)

    @staticmethod
    def verify_comment_content(
                test_case: TestCase, opinion: Opinion, comment: Comment,
                response: HttpResponse
            ):
        """
        Verify comment page content for user
        :param test_case: TestCase instance
        :param opinion: expected opinion
        :param comment: expected comment
        :param response: opinion response
        """
        test_case.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )

        # check comment card
        cards = soup.find_all(id=f'id--comment-card-{comment.id}')
        test_case.assertEqual(len(cards), 1)
        for child in cards[0].descendants:
            if isinstance(child, Tag):
                if child.name == 'img':
                    # author avatar
                    SoupMixin.in_tag_attr(child, 'alt', opinion.user.username)
                elif child.name == 'a' and \
                        child.id == f'id--comment-avatar-link-{comment.id}':
                    # user link
                    SoupMixin.in_tag_attr(
                        child, 'href', reverse_q(
                            namespaced_url(
                                USER_APP_NAME, USER_ID_ROUTE_NAME),
                            args=[opinion.user.id]))
                    test_case.assertIn(comment.user.username, child.text)
                elif child.id == f'id--comment-content-{comment.id}':
                    # comment content
                    test_case.assertEqual(child.text, comment.content)
