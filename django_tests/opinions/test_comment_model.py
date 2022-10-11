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

from datetime import datetime, timezone

from categories import STATUS_DRAFT
from categories.models import Status
from django_tests.opinions.base_opinion_test_cls import BaseOpinionTest
from opinions.models import Comment


class TestCommentModel(BaseOpinionTest):
    """
    Test status
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestCommentModel, TestCommentModel).setUpTestData()

    def test_comment_defaults(self):
        user, _ = TestCommentModel.get_user_by_index(0)
        opinion = TestCommentModel.opinions[0]
        kwargs = {
            Comment.OPINION_FIELD: opinion,
            Comment.USER_FIELD: user,
            Comment.STATUS_FIELD: Status.objects.get(name=STATUS_DRAFT),
        }
        comment = Comment.objects.create(**kwargs)
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, '')
        self.assertLessEqual(comment.created, datetime.now(tz=timezone.utc))
        self.assertLessEqual(comment.updated, datetime.now(tz=timezone.utc))
