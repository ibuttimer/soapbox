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

from user.queries import is_moderator, is_author
from opinions.views.utils import opinion_permissions, add_opinion_context
from categories.views import category_permissions
from .constants import COPYRIGHT_YEAR, COPYRIGHT, CSS_TEST_PATH_PREFIX
from .settings import DEVELOPMENT, TEST, GOOGLE_SITE_VERIFICATION

Social = namedtuple("Social", ["name", "icon", "url"])


def footer_context(request: HttpRequest) -> dict:
    """
    Context processor providing basic footer info
    :param request: http return
    :return: dictionary to add to template context
    """
    context = {
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
        "is_moderator": is_moderator(request.user),
        "is_author": is_author(request.user),
        "is_development": DEVELOPMENT,
        "is_test": TEST,
        "google_site_verification": GOOGLE_SITE_VERIFICATION
    }
    # add content permissions; key `<model_name>_<crud_op>` with boolean value
    opinion_permissions(request, context=context)
    category_permissions(request, context=context)
    # add general context updates
    add_opinion_context(request, context=context)
    return context


def test_context(request: HttpRequest) -> dict:
    """
    Context processor to add test related context
    :param request: http return
    :return: dictionary to add to template context
    """
    return {
        "css_test": request.path.index(CSS_TEST_PATH_PREFIX) >= 0
    }
