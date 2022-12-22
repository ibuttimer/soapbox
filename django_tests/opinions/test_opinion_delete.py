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

from opinions.models import Opinion, Comment
from user.models import User
from .base_opinion_test_cls import BaseOpinionTest
from .opinion_mixin_test_cls import OpinionMixin, AccessBy
from ..category_mixin_test_cls import CategoryMixin
from ..soup_mixin import SoupMixin


class TestOpinionDelete(
        SoupMixin, CategoryMixin, OpinionMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionDelete, cls).setUpTestData()

    def test_not_logged_in_access_by_id(self):
        """ Test must be logged in to access opinion by id """
        response = self.delete_opinion_by_id(self.opinions[0].id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_logged_in_access_by_slug(self):
        """ Test must be logged in to access opinion by slug """
        response = self.delete_opinion_by_slug(self.opinions[0].slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def check_delete_own_opinion(self, opinion: Opinion, access_by: AccessBy):
        """ Test delete opinion of logged-in user """
        _ = self.login_user_by_id(opinion.user.id)

        identifier = opinion.id if access_by == AccessBy.BY_ID else \
            opinion.slug

        response = self.delete_opinion_by(identifier, access_by)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.delete_opinion_by_id(opinion.id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def get_non_deleted_opinion(
            self, reported: bool = False, hidden: bool = False
    ) -> Optional[Opinion]:
        """
        Get an opinion which is not deleted
        :param reported: required reported status; default False not reported
        :param hidden: required hidden status; default False not hidden
        :return: opinion or None
        """
        opinion = None
        for opin in self.opinions:
            if opin.id in self.reported_opinion_set != reported:
                continue    # skip not correct reported status
            if opin.id in self.hidden_opinion_set != hidden:
                continue    # skip not correct hidden status
            if not self.is_opinion_deleted(opin.id):
                opinion = opin
                break
        return opinion

    def test_delete_own_opinion_by_id(self):
        """ Test delete opinion by id of logged-in user """
        opinion = self.get_non_deleted_opinion()
        self.assertIsNotNone(opinion)
        self.check_delete_own_opinion(opinion, AccessBy.BY_ID)

    def test_delete_own_opinion_by_slug(self):
        """ Test delete opinion by slug of logged-in user """
        opinion = self.get_non_deleted_opinion()
        self.assertIsNotNone(opinion)
        self.check_delete_own_opinion(opinion, AccessBy.BY_SLUG)

    def get_sub_level_comment(
        self, opinion_user: User = None, level: int = 0
    ) -> Optional[Comment]:
        """
        Get a comment with the specified level
        :param opinion_user: author of opinion: default None
        :param level: comment level; default 0
        :return: comment or None
        """
        comment = None
        current_level = 0
        for cmt in self.comments:
            if cmt.id in self.reported_comment_set:
                continue    # skip reported
            if opinion_user and cmt.opinion.user.id != opinion_user.id:
                continue    # wrong opinion user
            if current_level == cmt.level:
                next_level = current_level + 1
                if next_level > level:
                    if not self.is_opinion_deleted(cmt.opinion.id):
                        # related opinion not deleted so choose this one
                        comment = cmt
                        break
                    else:
                        next_level = current_level  # keep looking

                current_level = next_level

        return comment

    def check_delete_own_opinion_plus_comments_by_id(
            self, access_by: AccessBy):
        """ Check delete opinion and any comments by id of logged-in user """
        user = self.login_user_by_key()

        comment = self.get_sub_level_comment(user, level=1)
        self.assertIsNotNone(comment, 'Comment not found')

        # get the list of comment ids
        opinion = Opinion.objects.filter(**{
            f'{Opinion.id_field()}': comment.opinion.id
        }).first()
        self.assertIsNotNone(
            opinion, f'Opinion[{comment.opinion.id}] not found')

        comment_ids = []
        cmt_id = comment.id
        while cmt_id != Comment.NO_PARENT:
            comment = Comment.objects.filter(**{
                f'{Comment.id_field()}': cmt_id
            }).first()
            self.assertIsNotNone(
                comment, f'Comment[{cmt_id}] not found')
            comment_ids.append(cmt_id)
            cmt_id = comment.parent

        self.check_delete_own_opinion(opinion, access_by)

        # check comments were deleted as well
        for cmt_id in comment_ids:
            self.assertTrue(
                self.is_comment_deleted(cmt_id),
                f'Comment[{cmt_id}] not deleted'
            )

    def test_delete_own_opinion_plus_comments_by_id(self):
        """ Test delete opinion and any comments by id of logged-in user """
        self.check_delete_own_opinion_plus_comments_by_id(AccessBy.BY_ID)

    def test_delete_own_opinion_plus_comments_by_slug(self):
        """ Test delete opinion and any comments by slug of logged-in user """
        self.check_delete_own_opinion_plus_comments_by_id(AccessBy.BY_SLUG)

    def check_delete_other_opinion(
            self, opinion: Opinion, access_by: AccessBy):
        """ Test delete opinion of not logged-in user """
        self.login_user(self, self.get_other_user(opinion.user))

        identifier = opinion.id if access_by == AccessBy.BY_ID else \
            opinion.slug

        response = self.delete_opinion_by(identifier, access_by)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_other_opinion_by_id(self):
        """ Test delete opinion by id of not logged-in user """
        opinion = self.get_non_deleted_opinion()
        self.assertIsNotNone(opinion)
        self.check_delete_other_opinion(opinion, AccessBy.BY_ID)

    def test_delete_other_opinion_by_slug(self):
        """ Test page content for opinion by slug of not logged-in user """
        opinion = self.get_non_deleted_opinion()
        self.assertIsNotNone(opinion)
        self.check_delete_other_opinion(opinion, AccessBy.BY_SLUG)
