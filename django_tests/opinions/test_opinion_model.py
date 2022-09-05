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
import os
from datetime import datetime, timezone, MINYEAR

import django

from opinions.common import STATUS
from opinions.models import Opinion, Status

# 'allauth' checks for 'django.contrib.sites', so django must be setup before
# test
os.environ.setdefault("ENV_FILE", ".test-env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soapbox.settings")
django.setup()

from django.test import TestCase    # noqa


class TestOpinionModel(TestCase):
    """
    Test opinion
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_opinion_defaults(self):
        kwargs = {
            STATUS: Status.objects.get(name='Draft')
        }
        opinion = Opinion.objects.create(**kwargs)
        self.assertIsNotNone(opinion)
        self.assertEqual(opinion.title, '')
        self.assertEqual(opinion.content, '')
        self.assertEqual(opinion.slug, '')
        self.assertLess(opinion.created, datetime.now(tz=timezone.utc))
        self.assertLess(opinion.updated, datetime.now(tz=timezone.utc))
        self.assertEqual(opinion.published,
                         datetime(MINYEAR, 1, 1, 0, 0, tzinfo=timezone.utc))
