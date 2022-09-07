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
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    NAME_FIELD, DESCRIPTION_FIELD
)


class Category(models.Model):
    """ Categories model """

    MODEL_NAME = 'Category'

    # field names
    NAME_FIELD = NAME_FIELD
    DESCRIPTION_FIELD = DESCRIPTION_FIELD

    CATEGORY_ATTRIB_NAME_MAX_LEN: int = 40
    CATEGORY_ATTRIB_DESCRIPTION_MAX_LEN: int = 100

    name = models.CharField(_('name'), max_length=CATEGORY_ATTRIB_NAME_MAX_LEN,
                            unique=True)

    description = models.CharField(
        _('description'), max_length=CATEGORY_ATTRIB_DESCRIPTION_MAX_LEN,
        blank=True)

    class Meta:
        ordering = [NAME_FIELD]

    def __str__(self):
        return self.name


class Status(models.Model):
    """ Statuses model """

    MODEL_NAME = 'Status'

    # field names
    NAME_FIELD = NAME_FIELD

    STATUS_ATTRIB_NAME_MAX_LEN: int = 40

    name = models.CharField(_('name'), max_length=STATUS_ATTRIB_NAME_MAX_LEN,
                            blank=False, unique=True)

    class Meta:
        ordering = [NAME_FIELD]

    def __str__(self):
        return self.name
