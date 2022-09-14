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

from collections import namedtuple

from django.http import HttpRequest

from user.constants import MODERATOR_GROUP, AUTHOR_GROUP
from .constants import COPYRIGHT_YEAR, COPYRIGHT

Social = namedtuple("Social", ["name", "icon", "url"])


def footer_context(request: HttpRequest) -> dict:
    """
    Context processor providing basic footer info
    :param request: http return
    :return: dictionary to add to template context
    """
    return {
        "copyright_year": COPYRIGHT_YEAR,
        "copyright": COPYRIGHT,
        "socials": [
            Social("Facebook", "fa-brands fa-square-facebook",
                   "https://facebook.com"),
            Social("Twitter", "fa-brands fa-square-twitter",
                   "https://twitter.com"),
            Social("Instagram", "fa-brands fa-square-instagram",
                   "https://instagram.com"),
        ],
        "is_super": request.user.is_superuser,
        "is_moderator": request.user.groups.filter(
            name=MODERATOR_GROUP).exists(),
        "is_author": request.user.groups.filter(
            name=AUTHOR_GROUP).exists(),
    }
