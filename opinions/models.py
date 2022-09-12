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
from datetime import datetime, MINYEAR, timezone

from django.db import models
from django.utils.translation import gettext_lazy as _

from user.models import User
from categories.models import Category, Status
from utils import SlugMixin
from .constants import (
    TITLE_FIELD, CONTENT_FIELD, CATEGORIES_FIELD, STATUS_FIELD,
    USER_FIELD, SLUG_FIELD, CREATED_FIELD, UPDATED_FIELD,
    PUBLISHED_FIELD
)


class Opinion(SlugMixin, models.Model):
    """ Opinions model """

    MODEL_NAME = 'Opinion'

    # field names
    TITLE_FIELD = TITLE_FIELD
    CONTENT_FIELD = CONTENT_FIELD
    CATEGORIES_FIELD = CATEGORIES_FIELD
    STATUS_FIELD = STATUS_FIELD
    USER_FIELD = USER_FIELD
    SLUG_FIELD = SLUG_FIELD
    CREATED_FIELD = CREATED_FIELD
    UPDATED_FIELD = UPDATED_FIELD
    PUBLISHED_FIELD = PUBLISHED_FIELD

    OPINION_ATTRIB_TITLE_MAX_LEN: int = 100
    OPINION_ATTRIB_CONTENT_MAX_LEN: int = 1500
    OPINION_ATTRIB_SLUG_MAX_LEN: int = 50

    title = models.CharField(
        _('title'), max_length=OPINION_ATTRIB_TITLE_MAX_LEN, blank=False,
        unique=True)

    content = models.CharField(
        _('content'), max_length=OPINION_ATTRIB_CONTENT_MAX_LEN, blank=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    categories = models.ManyToManyField(Category)

    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    slug = models.SlugField(
        _('slug'), max_length=OPINION_ATTRIB_SLUG_MAX_LEN, blank=False,
        unique=True)

    # TODO is img field required?

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(
        default=datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))

    class Meta:
        ordering = [TITLE_FIELD]

    def __str__(self):
        return self.title

    def set_slug(self, title: str):
        """
        Set slug from specified title
        :param title: title to generate slug from
        """
        self.slug = Opinion.generate_unique_slug(
            self, Opinion.OPINION_ATTRIB_SLUG_MAX_LEN, title)
