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
from typing import Type, Optional

from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import truncatechars

from user.models import User
from categories.models import Category, Status
from utils import SlugMixin
from .constants import (
    ID_FIELD, TITLE_FIELD, CONTENT_FIELD, EXCERPT_FIELD, CATEGORIES_FIELD,
    STATUS_FIELD, USER_FIELD, SLUG_FIELD, CREATED_FIELD, UPDATED_FIELD,
    PUBLISHED_FIELD, PARENT_FIELD, LEVEL_FIELD,
    OPINION_FIELD, REQUESTED_FIELD, REASON_FIELD,
    REVIEWER_FIELD, COMMENT_FIELD, RESOLVED_FIELD,
    CLOSE_REVIEW_PERM, WITHDRAW_REVIEW_PERM, DESC_LOOKUP
)


class Opinion(SlugMixin, models.Model):
    """ Opinions model """

    MODEL_NAME = 'Opinion'

    # field names
    ID_FIELD = ID_FIELD
    TITLE_FIELD = TITLE_FIELD
    CONTENT_FIELD = CONTENT_FIELD
    EXCERPT_FIELD = EXCERPT_FIELD
    CATEGORIES_FIELD = CATEGORIES_FIELD
    STATUS_FIELD = STATUS_FIELD
    USER_FIELD = USER_FIELD
    SLUG_FIELD = SLUG_FIELD
    CREATED_FIELD = CREATED_FIELD
    UPDATED_FIELD = UPDATED_FIELD
    PUBLISHED_FIELD = PUBLISHED_FIELD
    ALL_FIELDS = [
        ID_FIELD, TITLE_FIELD, CONTENT_FIELD, EXCERPT_FIELD,
        CATEGORIES_FIELD, STATUS_FIELD, USER_FIELD, SLUG_FIELD,
        CREATED_FIELD, UPDATED_FIELD, PUBLISHED_FIELD
    ]

    SEARCH_DATE_FIELD = PUBLISHED_FIELD
    DATE_FIELDS = [CREATED_FIELD, UPDATED_FIELD, PUBLISHED_FIELD]

    OPINION_ATTRIB_TITLE_MAX_LEN: int = 100
    OPINION_ATTRIB_CONTENT_MAX_LEN: int = 2500
    OPINION_ATTRIB_EXCERPT_MAX_LEN: int = 150
    OPINION_ATTRIB_SLUG_MAX_LEN: int = 50

    title = models.CharField(
        _('title'), max_length=OPINION_ATTRIB_TITLE_MAX_LEN, blank=False,
        unique=True)

    # TODO ensure opinion content safe before saving to database

    content = models.CharField(
        _('content'), max_length=OPINION_ATTRIB_CONTENT_MAX_LEN, blank=False)

    excerpt = models.CharField(
        _('excerpt'), max_length=OPINION_ATTRIB_EXCERPT_MAX_LEN, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    categories = models.ManyToManyField(Category)

    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    slug = models.SlugField(
        _('slug'), max_length=OPINION_ATTRIB_SLUG_MAX_LEN, blank=False,
        unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(
        default=datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))

    class Meta:
        ordering = [TITLE_FIELD]

    def __str__(self):
        return f'{Opinion.MODEL_NAME}[{self.id}]:' \
               f'{truncatechars(self.title, 20)} {self.status.short_name}'

    def set_slug(self, title: str):
        """
        Set slug from specified title
        :param title: title to generate slug from
        """
        self.slug = Opinion.generate_unique_slug(
            self, Opinion.OPINION_ATTRIB_SLUG_MAX_LEN, title)

    @staticmethod
    def is_date_field(field: str):
        return field in Opinion.DATE_FIELDS

    @staticmethod
    def is_date_lookup(lookup: str):
        """
        Check if the specified `lookup` represents a date Lookup
        :param lookup: lookup string
        :return: True if lookup contains a date field
        """
        return any(
            map(lambda fld: fld in lookup, Opinion.DATE_FIELDS)
        )


class Comment(SlugMixin, models.Model):
    """ Opinions model """

    MODEL_NAME = 'Comment'

    NO_PARENT = 0
    """ Value representing no parent """

    # field names
    ID_FIELD = ID_FIELD
    CONTENT_FIELD = CONTENT_FIELD
    OPINION_FIELD = OPINION_FIELD
    PARENT_FIELD = PARENT_FIELD
    LEVEL_FIELD = LEVEL_FIELD
    USER_FIELD = USER_FIELD
    STATUS_FIELD = STATUS_FIELD
    SLUG_FIELD = SLUG_FIELD
    CREATED_FIELD = CREATED_FIELD
    UPDATED_FIELD = UPDATED_FIELD
    PUBLISHED_FIELD = PUBLISHED_FIELD

    SEARCH_DATE_FIELD = PUBLISHED_FIELD
    DATE_FIELDS = [CREATED_FIELD, UPDATED_FIELD, PUBLISHED_FIELD]

    COMMENT_ATTRIB_CONTENT_MAX_LEN: int = 700
    COMMENT_ATTRIB_SLUG_MAX_LEN: int = Opinion.OPINION_ATTRIB_SLUG_MAX_LEN

    content = models.CharField(
        _('content'), max_length=COMMENT_ATTRIB_CONTENT_MAX_LEN, blank=False)

    # TODO ensure comment content safe before saving to database

    opinion = models.ForeignKey(Opinion, on_delete=models.CASCADE)

    parent = models.BigIntegerField(
        _('parent'), default=NO_PARENT, blank=True)

    level = models.IntegerField(_('level'), default=0, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    slug = models.SlugField(
        _('slug'), max_length=COMMENT_ATTRIB_SLUG_MAX_LEN, blank=False,
        unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(
        default=datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))

    class Meta:
        ordering = [ID_FIELD]

    def __str__(self):
        return f'{Comment.MODEL_NAME}[{self.id}]:' \
               f'{truncatechars(self.content, 20)} {self.status.short_name}'

    def set_slug(self, content: str):
        """
        Set slug from specified content
        :param content: content to generate slug from
        """
        self.slug = Comment.generate_unique_slug(
            self, Comment.COMMENT_ATTRIB_SLUG_MAX_LEN, strip_tags(content))

    @staticmethod
    def is_date_field(field: str):
        return field in Comment.DATE_FIELDS

    @staticmethod
    def is_date_lookup(lookup: str):
        """
        Check if the specified `lookup` represents a date Lookup
        :param lookup: lookup string
        :return: True if lookup contains a date field
        """
        return any(
            map(lambda fld: fld in lookup, Comment.DATE_FIELDS)
        )


class Review(models.Model):
    """ Reviews model """

    MODEL_NAME = 'Review'

    # field names
    ID_FIELD = ID_FIELD
    OPINION_FIELD = OPINION_FIELD
    COMMENT_FIELD = COMMENT_FIELD
    REQUESTED_FIELD = REQUESTED_FIELD
    REASON_FIELD = REASON_FIELD
    REVIEWER_FIELD = REVIEWER_FIELD
    STATUS_FIELD = STATUS_FIELD
    CREATED_FIELD = CREATED_FIELD
    UPDATED_FIELD = UPDATED_FIELD
    RESOLVED_FIELD = RESOLVED_FIELD

    REVIEW_ATTRIB_REASON_MAX_LEN: int = 500

    opinion = models.ForeignKey(
        Opinion, null=True, blank=True, on_delete=models.CASCADE)

    comment = models.ForeignKey(
        Comment, null=True, blank=True, on_delete=models.CASCADE)

    requested = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='requested_by')

    reason = models.CharField(
        _('reason'), max_length=REVIEW_ATTRIB_REASON_MAX_LEN, blank=False)

    reviewer = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE,
        related_name='reviewed_by')

    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    resolved = models.DateTimeField(
        default=datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))

    @classmethod
    def content_field(cls, model: Type[models.Model]) -> Optional[str]:
        """
        Return the name of the content field for the specified model
        :param model: model to get field for
        :return: field name or None
        """
        return Review.OPINION_FIELD if isinstance(model, Opinion) else \
            Review.COMMENT_FIELD if isinstance(model, Comment) else None

    class Meta:
        permissions = [
            (CLOSE_REVIEW_PERM,
             "Can close a review by setting its status to resolved"),
            (WITHDRAW_REVIEW_PERM,
             "Can close a review by setting its status to withdrawn"),
        ]

    def __str__(self):
        return f'{Review.MODEL_NAME}[{self.id}]: {self.opinion} - ' \
               f'{self.status.short_name}'


class AgreementStatus(models.Model):
    """ AgreementStatus model """

    MODEL_NAME = 'AgreementStatus'

    # field names
    ID_FIELD = ID_FIELD
    OPINION_FIELD = OPINION_FIELD
    COMMENT_FIELD = COMMENT_FIELD
    USER_FIELD = USER_FIELD
    STATUS_FIELD = STATUS_FIELD
    UPDATED_FIELD = UPDATED_FIELD

    opinion = models.ForeignKey(
        Opinion, null=True, blank=True, on_delete=models.CASCADE)

    comment = models.ForeignKey(
        Comment, null=True, blank=True, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def content_field(cls, model: Type[models.Model]) -> Optional[str]:
        """
        Return the name of the content field for the specified model
        :param model: model to get field for
        :return: field name or None
        """
        return AgreementStatus.OPINION_FIELD if isinstance(model, Opinion) \
            else AgreementStatus.COMMENT_FIELD if isinstance(model, Comment) \
            else None

    def __str__(self):
        return f'{AgreementStatus.MODEL_NAME}[{self.id}]: ' \
               f'{self.opinion if self.opinion else self.comment} - ' \
               f'{self.status.short_name}'


class HideStatus(models.Model):
    """ HideStatus model """

    MODEL_NAME = 'HideStatus'

    # field names
    ID_FIELD = ID_FIELD
    OPINION_FIELD = OPINION_FIELD
    COMMENT_FIELD = COMMENT_FIELD
    USER_FIELD = USER_FIELD
    UPDATED_FIELD = UPDATED_FIELD

    opinion = models.ForeignKey(
        Opinion, null=True, blank=True, on_delete=models.CASCADE)

    comment = models.ForeignKey(
        Comment, null=True, blank=True, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def content_field(cls, model: Type[models.Model]) -> Optional[str]:
        """
        Return the name of the content field for the specified model
        :param model: model to get field for
        :return: field name or None
        """
        return HideStatus.OPINION_FIELD if isinstance(model, Opinion) \
            else HideStatus.COMMENT_FIELD if isinstance(model, Comment) \
            else None

    def __str__(self):
        return f'{HideStatus.MODEL_NAME}[{self.id}]: ' \
               f'{self.opinion if self.opinion else self.comment}'


class PinStatus(models.Model):
    """ PinStatus model """

    MODEL_NAME = 'PinStatus'

    # field names
    ID_FIELD = ID_FIELD
    OPINION_FIELD = OPINION_FIELD
    USER_FIELD = USER_FIELD
    UPDATED_FIELD = UPDATED_FIELD

    opinion = models.ForeignKey(
        Opinion, null=True, blank=True, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{PinStatus.MODEL_NAME}[{self.id}]: {self.opinion}'


def is_id_lookup(lookup: str):
    """
    Check if the specified `lookup` represents an id Lookup
    :param lookup: lookup string
    :return: True if lookup contains the field
    """
    lookup = lookup.lower()
    return lookup == ID_FIELD or lookup == f'{DESC_LOOKUP}{ID_FIELD}'
