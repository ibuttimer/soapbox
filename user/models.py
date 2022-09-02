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

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField

from soapbox import AVATAR_FOLDER, DEVELOPMENT

from .common import (
    FIRST_NAME, LAST_NAME, BIO, AVATAR, CATEGORIES
)


class User(AbstractUser):
    """
    Custom user model
    (Recommended by
    https://docs.djangoproject.com/en/4.1/topics/auth/customizing/#auth-custom-user)
    """

    MODEL_NAME = 'User'
    # field names
    FIRST_NAME_FIELD = FIRST_NAME
    LAST_NAME_FIELD = LAST_NAME
    # EMAIL_FIELD and USERNAME_FIELD inherited from AbstractUser
    PASSWORD_FIELD = 'password'
    BIO_FIELD = BIO
    AVATAR_FIELD = AVATAR
    CATEGORIES_FIELD = CATEGORIES

    AVATAR_BLANK = 'avatar_blank'

    # Values copied from django.contrib.auth.models.py::AbstractUser
    USER_ATTRIB_FIRST_NAME_MAX_LEN: int = 150
    USER_ATTRIB_LAST_NAME_MAX_LEN: int = 150
    USER_ATTRIB_USERNAME_MAX_LEN: int = 150
    # Values copied from django.db.models.fields::EmailField
    USER_ATTRIB_EMAIL_MAX_LEN: int = 254
    # Values copied from cloudinary.models::CloudinaryField
    USER_ATTRIB_AVATAR_MAX_LEN: int = 255

    USER_ATTRIB_BIO_MAX_LEN: int = 250
    USER_ATTRIB_CATEGORIES_MAX_LEN: int = 250

    bio = models.CharField(_('biography'), max_length=USER_ATTRIB_BIO_MAX_LEN)

    # ImageField for local dev, CloudinaryField for production
    # https://cloudinary.com/documentation/django_image_and_video_upload#django_forms_and_models
    avatar = models.ImageField(
        _('image'), default=AVATAR_BLANK, upload_to=AVATAR_FOLDER, blank=True
    ) if DEVELOPMENT else CloudinaryField(
        _('image'), default=AVATAR_BLANK, folder=AVATAR_FOLDER)

    categories = models.CharField(
        _('categories'), max_length=USER_ATTRIB_CATEGORIES_MAX_LEN, blank=True)

    class Meta:
        ordering = ["date_joined"]

    def __str__(self):
        return self.username
