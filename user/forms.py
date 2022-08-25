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
from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm

from .models import (
    USER_ATTRIB_FIRST_NAME_MAX_LEN, USER_ATTRIB_LAST_NAME_MAX_LEN, User
)


class UserSignupForm(SignupForm):
    """ Custom user sign up form """

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)

        # add first & last name fields
        self.fields["first_name"] = forms.CharField(
            label=_("First name"),
            max_length=USER_ATTRIB_FIRST_NAME_MAX_LEN,
            widget=forms.TextInput(attrs={"placeholder": _("First name")}),
        )
        self.fields["last_name"] = forms.CharField(
            label=_("Last name"),
            max_length=USER_ATTRIB_LAST_NAME_MAX_LEN,
            widget=forms.TextInput(attrs={"placeholder": _("Last name")}),
        )

        # reorder fields so first & last name appear at start
        self.fields.move_to_end("last_name", last=False)
        self.fields.move_to_end("first_name", last=False)

    def signup(self, request: HttpRequest, user: User) -> None:
        """
        Perform custom signup actions
        :param request:
        :param user: user object
        """
        pass
