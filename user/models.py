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
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Values copied from django.contrib.auth.models.py::AbstractUser
USER_ATTRIB_FIRST_NAME_MAX_LEN: int = 150
USER_ATTRIB_LAST_NAME_MAX_LEN: int = 150
USER_ATTRIB_USERNAME_MAX_LEN: int = 150
# Values copied from django.db.models.fields::EmailField
USER_ATTRIB_EMAIL_MAX_LEN: int = 254


class Contributor(User):
    """
    Contributor model
    """
    bio = models.CharField(max_length=250)

    # https://cloudinary.com/documentation/django_image_and_video_upload#django_forms_and_models
    avatar = CloudinaryField('image', default='placeholder', folder="soapbox")

    categories = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["date_joined"]

    def __str__(self):
        return self.username
