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
from django.dispatch import receiver
from allauth.account.signals import (
    user_logged_in, user_logged_out, user_signed_up
)
from allauth.socialaccount.signals import (
    pre_social_login, social_account_added, social_account_updated,
    social_account_removed
)

from opinions.notifications import process_login_opinions
from .permissions import add_to_authors


@receiver(user_logged_in)
def user_logged_in_callback(sender, **kwargs):
    print("user_logged_in!")

    process_login_opinions(
        kwargs.get('request', None), kwargs.get('user', None))


@receiver(user_logged_out)
def user_logged_out_callback(sender, **kwargs):
    print("user_logged_out!")


@receiver(user_signed_up)
def user_signed_up_callback(sender, **kwargs):
    print("user_signed_up!")
    add_to_authors(kwargs['user'])


@receiver(pre_social_login)
def pre_social_login_callback(sender, **kwargs):
    print("pre_social_login!")


@receiver(social_account_added)
def social_account_added_callback(sender, **kwargs):
    print("social_account_added!")


@receiver(social_account_updated)
def social_account_updated_callback(sender, **kwargs):
    print("social_account_updated!")


@receiver(social_account_removed)
def social_account_removed_callback(sender, **kwargs):
    print("social_account_removed!")
