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

from opinions.notifications import (
    process_login_opinions, process_register_new_user
)
from .models import User
from .permissions import add_to_authors


@receiver(user_logged_in)
def user_logged_in_callback(sender, **kwargs):
    # by the time this signal is received the 'last_login' field in
    # AbstractBaseUser has already been updated to the current login

    user: User = kwargs.get('user', None)
    if user:
        process_login_opinions(kwargs.get('request', None), user)


@receiver(user_logged_out)
def user_logged_out_callback(sender, **kwargs):
    user: User = kwargs.get('user', None)
    if user:
        # update previous login
        user.previous_login = user.last_login
        user.save(update_fields=[User.PREVIOUS_LOGIN_FIELD])


@receiver(user_signed_up)
def user_signed_up_callback(sender, **kwargs):
    user: User = kwargs.get('user', None)
    if user:
        add_to_authors(user)
        process_register_new_user(kwargs.get('request', None), user)

@receiver(pre_social_login)
def pre_social_login_callback(sender, **kwargs):
    pass


@receiver(social_account_added)
def social_account_added_callback(sender, **kwargs):
    pass


@receiver(social_account_updated)
def social_account_updated_callback(sender, **kwargs):
    pass


@receiver(social_account_removed)
def social_account_removed_callback(sender, **kwargs):
    pass
