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
from opinions.constants import UNDER_REVIEW_COMMENT_CONTENT, \
    COMMENT_ID_ROUTE_NAME, COMMENT_SLUG_ROUTE_NAME
from opinions.models import Opinion, Comment
from soapbox import OPINIONS_APP_NAME, USER_APP_NAME
from user import USER_ID_ROUTE_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .base_comment_test import BaseCommentTest
from ..category_mixin import CategoryMixin
from ..soup_mixin import SoupMixin
from ..user.base_user_test import BaseUserTest

COMMENT_VIEW_TEMPLATE = f'{OPINIONS_APP_NAME}/comment_view.html'
OPINION_VIEW_COMMENTS_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/snippet/view_comments.html'
OPINION_COMMENTS_BUNDLE_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/snippet/comment_bundle.html'
OPINION_COMMENTS_REACTIONS_TEMPLATE = \
    f'{OPINIONS_APP_NAME}/snippet/reactions.html'

BY_ID = 'id'
BY_SLUG = 'slug'


class TestCommentView(SoupMixin, CategoryMixin, BaseCommentTest):
    """
    Test comment page view
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

    def get_comment_by_id(self, pk: int) -> HttpResponse:
        """
        Get the comment page
        :param pk: id of comment
        """
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, COMMENT_ID_ROUTE_NAME),
                args=[pk]))

    def get_comment_by_slug(self, slug: str) -> HttpResponse:
        """
        Get the comment page
        :param slug: slug of comment
        """
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, COMMENT_SLUG_ROUTE_NAME),
                args=[slug]))

    def get_comment_by(
            self, identifier: [int, str], comment_by: str) -> HttpResponse:
        """
        Get the comment page
        :param identifier: comment identifier
        :param comment_by: method of accessing opinion; 'id' or 'slug'
        :returns response
        """
        get_by = self.get_comment_by_id \
            if comment_by == BY_ID else self.get_comment_by_slug
        return get_by(identifier)

    def get_other_users_comments(
            self, not_me: User, status: str) -> list[Comment]:
        """
        Get a list of other users' comments with the specified status
        :param not_me: user to
        :param status: required status
        :return: list of comments
        """
        # get list of other users' published comments
        comments = list(
            filter(lambda cmt: cmt.user.id != not_me.id
                   and cmt.status.name == status,
                   TestCommentView.comments)
        )
        self.assertGreaterEqual(
            len(comments), 1, msg=f'No comments with {status} status')
        return comments

    def check_get_other_comment(self, comment_by: str):
        """ Test comment content of not logged-in user """
        _, key = TestCommentView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        # get list of other users' published comments
        comments = self.get_other_users_comments(
            logged_in_user, STATUS_PUBLISHED)
        comment = comments[0]

        self.assertNotEqual(logged_in_user, comment.user)
        response = self.get_comment_by(
            comment.id if comment_by == BY_ID else comment.slug, comment_by)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for template in [
            COMMENT_VIEW_TEMPLATE, OPINION_VIEW_COMMENTS_TEMPLATE,
            OPINION_COMMENTS_BUNDLE_TEMPLATE,
            OPINION_COMMENTS_REACTIONS_TEMPLATE
        ]:
            self.assertTemplateUsed(response, template)

        comments = Comment.objects.filter(**{
            Comment.OPINION_FIELD: comment.opinion,
            Comment.PARENT_FIELD: Comment.NO_PARENT
        })
        TestCommentView.verify_comment_content(
            self, comments[0], response, user=logged_in_user)

        # TODO extend comment testing to comments on comments

    def test_get_other_comment_by_id(self):
        """ Test comment content by id of not logged-in user """
        self.check_get_other_comment(BY_ID)

    def test_get_other_comment_by_slug(self):
        """ Test comment content by slug of not logged-in user """
        self.check_get_other_comment(BY_SLUG)

    @staticmethod
    def verify_comment_content(test_case: TestCase, comment: Comment,
                               response: HttpResponse, user: User = None):
        """
        Verify comment page content for user
        :param test_case: TestCase instance
        :param comment: expected comment
        :param response: opinion response
        :param user: current user; default None
        """
        test_case.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )

        # comment author can always see their own
        under_review = user and comment.user != user
        if under_review:
            under_review = any(
                map(lambda op: op.id == comment.id,
                    test_case.reported_comments)
            )
        expected_content = UNDER_REVIEW_COMMENT_CONTENT \
            if under_review else comment.content

        # check comment card
        cards = soup.find_all(id=f'id--comment-card-{comment.id}')
        test_case.assertEqual(len(cards), 1)
        for child in cards[0].descendants:
            if isinstance(child, Tag):
                if child.name == 'img':
                    # author avatar
                    test_case.assertTrue(
                        SoupMixin.in_tag_attr(
                            child, 'alt', comment.user.username))
                elif child.name == 'a' and \
                        child.get('id') == \
                        f'id--comment-avatar-link-{comment.id}':
                    # user link
                    test_case.assertTrue(
                        SoupMixin.in_tag_attr(
                            child, 'href', reverse_q(
                                namespaced_url(
                                    USER_APP_NAME, USER_ID_ROUTE_NAME),
                                args=[comment.user.id])))
                    test_case.assertIn(comment.user.username, child.text)
                elif child.get('id') == f'id--comment-content-{comment.id}':
                    # comment content
                    test_case.assertEqual(
                        child.text.strip(), expected_content)
