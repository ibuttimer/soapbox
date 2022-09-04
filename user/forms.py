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
from cloudinary.forms import CloudinaryFileField
from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget

from opinions.models import Category
from soapbox import IMAGE_FILE_TYPES, DEVELOPMENT
from utils import update_field_widgets, error_messages, ErrorMsgs
from .models import User
from .common import (
    FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, PASSWORD_CONFIRM,
    BIO, AVATAR, CATEGORIES
)


class UserSignupForm(SignupForm):
    """ Custom user sign up form """

    FIRST_NAME_FF = FIRST_NAME
    LAST_NAME_FF = LAST_NAME
    EMAIL_FF = EMAIL
    USERNAME_FF = USERNAME
    PASSWORD_FF = PASSWORD
    PASSWORD_CONFIRM_FF = PASSWORD_CONFIRM

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)

        # add first & last name fields
        self.fields[UserSignupForm.FIRST_NAME_FF] = forms.CharField(
            label=_("First name"),
            max_length=User.USER_ATTRIB_FIRST_NAME_MAX_LEN,
            widget=forms.TextInput(attrs={
                "placeholder": _("User first name")
            }),
        )
        self.fields[UserSignupForm.LAST_NAME_FF] = forms.CharField(
            label=_("Last name"),
            max_length=User.USER_ATTRIB_LAST_NAME_MAX_LEN,
            widget=forms.TextInput(attrs={
                "placeholder": _("User last name")
            }),
        )

        # reorder fields so first & last name appear at start
        self.fields.move_to_end(UserSignupForm.LAST_NAME_FF, last=False)
        self.fields.move_to_end(UserSignupForm.FIRST_NAME_FF, last=False)

    class Meta:
        model = User
        fields = [
            FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, PASSWORD_CONFIRM
        ]

    def signup(self, request: HttpRequest, user: User) -> None:
        """
        Perform custom signup actions
        :param request:
        :param user: user object
        """
        pass


class NoCurrentClearableFileInput(forms.ClearableFileInput):
    """ Customised ClearableFileInput form with different template """
    template_name = "widgets/clearable_file_input.html"


class UserForm(forms.ModelForm):
    """
    Form to update a user.
    """

    FIRST_NAME_FF = FIRST_NAME
    LAST_NAME_FF = LAST_NAME
    EMAIL_FF = EMAIL
    BIO_FF = BIO
    AVATAR_FF = AVATAR
    CATEGORIES_FF = CATEGORIES

    first_name = forms.CharField(
        label=_("First name"),
        max_length=User.USER_ATTRIB_FIRST_NAME_MAX_LEN,
        required=False)
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=User.USER_ATTRIB_LAST_NAME_MAX_LEN,
        required=False)
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("E-mail address"),
                "autocomplete": "email",
            }
        )
    )

    bio = SummernoteTextField(blank=False)

    avatar_args = {
        "label": _("Avatar"),
        "required": False,
        "widget": NoCurrentClearableFileInput(attrs={
            # https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types#common_image_file_types
            "accept": ", ".join(IMAGE_FILE_TYPES)
        })
    }
    # ImageField for local dev, CloudinaryFileField for production
    avatar = forms.ImageField(
            **avatar_args
        ) if DEVELOPMENT else CloudinaryFileField(
            options={
                'folder': User.avatar.field.options['folder'],
            },
            **avatar_args
        )

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = [
            FIRST_NAME, LAST_NAME, EMAIL, BIO, AVATAR
        ]
        non_bootstrap_fields = [BIO, AVATAR]
        help_texts = {
            FIRST_NAME: 'User first name.',
            LAST_NAME: 'User last name.',
            EMAIL: 'Email address of user.',
            BIO: 'Biography of user.',
            AVATAR: 'User avatar',
        }
        error_messages = error_messages(
            model.MODEL_NAME,
            *[ErrorMsgs(field, max_length=True)
              for field in (FIRST_NAME, LAST_NAME)]
        )
        widgets = {
            BIO: SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in UserForm.Meta.fields
             if field not in UserForm.Meta.non_bootstrap_fields],
            {'class': 'form-control'})
