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

from opinions.models import HideStatus
from .base_opinion_test import BaseOpinionTest


class TestHideModel(BaseOpinionTest):
    """
    Test review
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestHideModel, TestHideModel).setUpTestData()

    def test_review_defaults(self):
        opinion = TestHideModel.opinions[0]
        user = TestHideModel.get_other_user(opinion.user)

        kwargs = {
            HideStatus.OPINION_FIELD: opinion,
            HideStatus.USER_FIELD: user,
        }
        hidden = HideStatus.objects.create(**kwargs)
        self.assertIsNotNone(hidden)
        self.assertEqual(hidden.opinion, opinion)
        self.assertIsNone(hidden.comment)
        self.assertLessEqual(hidden.updated, datetime.now(tz=timezone.utc))

        comment = TestHideModel.comments[0]
        user = TestHideModel.get_other_user(comment.user)

        kwargs = {
            HideStatus.COMMENT_FIELD: comment,
            HideStatus.USER_FIELD: user,
        }
        hidden = HideStatus.objects.create(**kwargs)
        self.assertIsNotNone(hidden)
        self.assertEqual(hidden.comment, comment)
        self.assertIsNone(hidden.opinion)
        self.assertLessEqual(hidden.updated, datetime.now(tz=timezone.utc))