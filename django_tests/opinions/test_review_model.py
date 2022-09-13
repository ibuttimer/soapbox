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
from datetime import datetime, timezone, MINYEAR

from categories import STATUS_DRAFT
from categories.models import Status
from opinions.models import Review
from .base_opinion_test_cls import BaseOpinionTest


class TestReviewModel(BaseOpinionTest):
    """
    Test review
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestReviewModel, TestReviewModel).setUpTestData()

    def test_review_defaults(self):
        requested, _ = TestReviewModel.get_user_by_index(0)
        reviewer, _ = TestReviewModel.get_user_by_index(1)
        opinion = TestReviewModel.opinions[0]
        kwargs = {
            Review.OPINION_FIELD: opinion,
            Review.REQUESTED_FIELD: requested,
            Review.REVIEWER_FIELD: reviewer,
            Review.STATUS_FIELD: Status.objects.get(name=STATUS_DRAFT),
        }
        review = Review.objects.create(**kwargs)
        self.assertIsNotNone(review)
        self.assertEqual(review.reason, '')
        self.assertEqual(review.comment, '')
        self.assertLessEqual(review.created, datetime.now(tz=timezone.utc))
        self.assertLessEqual(review.updated, datetime.now(tz=timezone.utc))
        self.assertEqual(review.resolved,
                         datetime(MINYEAR, 1, 1, 0, 0, tzinfo=timezone.utc))
