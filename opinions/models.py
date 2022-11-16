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
from utils import SlugMixin, ModelMixin, ModelFacadeMixin
from .constants import (
    ID_FIELD, TITLE_FIELD, CONTENT_FIELD, EXCERPT_FIELD, CATEGORIES_FIELD,
    STATUS_FIELD, USER_FIELD, SLUG_FIELD, CREATED_FIELD, UPDATED_FIELD,
    PUBLISHED_FIELD, PARENT_FIELD, LEVEL_FIELD,
    OPINION_FIELD, REQUESTED_FIELD, REASON_FIELD,
    REVIEWER_FIELD, COMMENT_FIELD, RESOLVED_FIELD, CLOSE_REVIEW_PERM,
    WITHDRAW_REVIEW_PERM, AUTHOR_FIELD
)


class Opinion(ModelFacadeMixin, ModelMixin, SlugMixin, models.Model):
    """ Opinions model """

    # field names
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
        return f'{truncatechars(self.title, 20)} {self.status.short_name}'

    def set_slug(self, title: str):
        """
        Set slug from specified title
        :param title: title to generate slug from
        """
        self.slug = Opinion.generate_unique_slug(
            self, Opinion.OPINION_ATTRIB_SLUG_MAX_LEN, title)

    @classmethod
    def date_fields(cls) -> list[str]:
        """ Get the list of date fields """
        return Opinion.DATE_FIELDS


assert Opinion.id_field() == ID_FIELD


class Comment(ModelFacadeMixin, ModelMixin, SlugMixin, models.Model):
    """ Opinions model """

    NO_PARENT = 0
    """ Value representing no parent """

    # field names
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
        return f'{truncatechars(self.content, 20)} {self.status.short_name}'

    def set_slug(self, content: str):
        """
        Set slug from specified content
        :param content: content to generate slug from
        """
        self.slug = Comment.generate_unique_slug(
            self, Comment.COMMENT_ATTRIB_SLUG_MAX_LEN, strip_tags(content))

    @classmethod
    def date_fields(cls) -> list[str]:
        """ Get the list of date fields """
        return Comment.DATE_FIELDS


assert Comment.id_field() == ID_FIELD


class OpinionCommentMixin:
    """ Mixin for models with both Comment and Opinion fields """

    @classmethod
    def content_field(
        cls, model: Type[ModelMixin], opinion: str = OPINION_FIELD,
        comment: str = COMMENT_FIELD
    ) -> Optional[str]:
        """
        Return the name of the content field for the specified model
        :param model: model to get field for
        :param opinion: model field name for opinion
        :param comment: model field name for comment
        :return: field name or None
        """
        model_name = ModelMixin.model_name_obj(model)
        return opinion if model_name == Opinion.model_name() else \
            comment if model_name == Comment.model_name() else None


class Review(OpinionCommentMixin, ModelMixin, models.Model):
    """ Reviews model """

    # field names
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

    class Meta:
        permissions = [
            (CLOSE_REVIEW_PERM,
             "Can close a review by setting its status to resolved"),
            (WITHDRAW_REVIEW_PERM,
             "Can close a review by setting its status to withdrawn"),
        ]

    def __str__(self):
        return f'{self.opinion} - {self.status.short_name}'


class AgreementStatus(OpinionCommentMixin, ModelMixin, models.Model):
    """ AgreementStatus model """

    # field names
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

    def __str__(self):
        return f'{self.opinion if self.opinion else self.comment} - ' \
               f'{self.status.short_name}'


class HideStatus(OpinionCommentMixin, ModelMixin, models.Model):
    """ HideStatus model """

    # field names
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

    def __str__(self):
        return f'Hide {self.opinion if self.opinion else self.comment}'


class PinStatus(ModelMixin, models.Model):
    """ PinStatus model """

    # field names
    OPINION_FIELD = OPINION_FIELD
    USER_FIELD = USER_FIELD
    UPDATED_FIELD = UPDATED_FIELD

    opinion = models.ForeignKey(
        Opinion, null=True, blank=True, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Pin {self.model_name()}[{self.id}]: {self.opinion}'


class FollowStatus(ModelMixin, models.Model):
    """ FollowStatus model """

    # field names
    AUTHOR_FIELD = AUTHOR_FIELD
    USER_FIELD = USER_FIELD
    UPDATED_FIELD = UPDATED_FIELD

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authored_by'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} following {self.author}'
