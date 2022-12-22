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
from typing import List

from allauth.socialaccount.models import SocialApp

from .constants import MODERATOR_GROUP, AUTHOR_GROUP
from .models import User


def is_moderator(user: User) -> bool:
    """
    Check if user is a moderator
    :param user: user to check
    :return: True if moderator
    """
    return user.groups.filter(name=MODERATOR_GROUP).exists() \
        if user else False


def is_author(user: User) -> bool:
    """
    Check if user is an author
    :param user: user to check
    :return: True if author
    """
    return user.groups.filter(name=AUTHOR_GROUP).exists() \
        if user else False


def get_social_providers() -> List[str]:
    """ Get a list of the social login providers """
    return SocialApp.objects.values_list('provider', flat=True)
