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
from typing import Optional

from opinions.models import Comment
from .base_opinion_test_cls import BaseOpinionTest
from .opinion_mixin_test_cls import OpinionMixin, AccessBy
from ..category_mixin_test_cls import CategoryMixin
from ..soup_mixin import SoupMixin


class TestCommentDelete(
        SoupMixin, CategoryMixin, OpinionMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestCommentDelete, cls).setUpTestData()

    def test_not_logged_in_access_by_id(self):
        """ Test must be logged in to access comment by id """
        response = self.delete_comment_by_id(self.comments[0].id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_logged_in_access_by_slug(self):
        """ Test must be logged in to access comment by slug """
        response = self.delete_comment_by_slug(self.comments[0].slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def check_delete_own_comment(self, comment: Comment, access_by: AccessBy):
        """ Test delete comment of logged-in user """
        _ = self.login_user_by_id(comment.user.id)

        identifier = comment.id if access_by == AccessBy.BY_ID else \
            comment.slug

        response = self.delete_comment_by(identifier, access_by)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def get_non_deleted_comment(
        self, reported: bool = False, hidden: bool = False
    ) -> Optional[Comment]:
        """
        Get a comment which is not deleted
        :param reported: required reported status; default False not reported
        :param hidden: required hidden status; default False not hidden
        :return: comment or None
        """
        comment = None
        for cmt in self.comments:
            if cmt.id in self.reported_comment_set != reported:
                continue    # skip not correct reported status
            if cmt.id in self.hidden_comment_set != hidden:
                continue    # skip not correct hidden status
            if not self.is_comment_deleted(cmt.id):
                comment = cmt
                break
        return comment

    def test_delete_own_comment_by_id(self):
        """ Test delete comment by id of logged-in user """
        comment = self.get_non_deleted_comment()
        self.assertIsNotNone(comment)
        self.check_delete_own_comment(comment, AccessBy.BY_ID)

    def test_delete_own_comment_by_slug(self):
        """ Test delete comment by slug of logged-in user """
        comment = self.get_non_deleted_comment()
        self.assertIsNotNone(comment)
        self.check_delete_own_comment(comment, AccessBy.BY_SLUG)

    def check_delete_other_comment(
            self, comment: Comment, access_by: AccessBy):
        """ Test delete comment of not logged-in user """
        self.login_user(self, self.get_other_user(comment.user))

        identifier = comment.id if access_by == AccessBy.BY_ID else \
            comment.slug

        response = self.delete_comment_by(identifier, access_by)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_other_comment_by_id(self):
        """ Test delete comment by id of not logged-in user """
        comment = self.get_non_deleted_comment()
        self.assertIsNotNone(comment)
        self.check_delete_other_comment(comment, AccessBy.BY_ID)

    def test_delete_other_comment_by_slug(self):
        """ Test page content for comment by slug of not logged-in user """
        comment = self.get_non_deleted_comment()
        self.assertIsNotNone(comment)
        self.check_delete_other_comment(comment, AccessBy.BY_SLUG)
