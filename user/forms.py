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

from soapbox import IMAGE_FILE_TYPES
from utils import update_field_widgets, error_messages, ErrorMsgs
from .models import User


_FIRST_NAME_FF = "first_name"
_LAST_NAME_FF = "last_name"
_EMAIL_FF = "email"
_USERNAME_FF = "username"
_PASSWORD_FF = "password1"
_BIO_FF = "bio"
_AVATAR_FF = "avatar"


class UserSignupForm(SignupForm):
    """ Custom user sign up form """

    FIRST_NAME_FF = _FIRST_NAME_FF
    LAST_NAME_FF = _LAST_NAME_FF
    EMAIL_FF = _EMAIL_FF
    USERNAME_FF = _USERNAME_FF
    PASSWORD_FF = _PASSWORD_FF

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

    FIRST_NAME_FF = _FIRST_NAME_FF
    LAST_NAME_FF = _LAST_NAME_FF
    EMAIL_FF = _EMAIL_FF
    BIO_FF = _BIO_FF
    AVATAR_FF = _AVATAR_FF

    @staticmethod
    def get_first_name_field_name():
        return UserForm.FIRST_NAME_FF

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

    bio = SummernoteTextField()

    # https://cloudinary.com/documentation/django_image_and_video_upload#django_forms_and_models
    avatar = CloudinaryFileField(
        label=_("Avatar"),
        required=False,
        options={
            'folder': User.avatar.field.options['folder'],
        },
        widget=NoCurrentClearableFileInput(attrs={
            # https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types#common_image_file_types
            "accept": ", ".join(IMAGE_FILE_TYPES)
        })
    )

    # categories = models.CharField(
    #     max_length=User.USER_ATTRIB_CATEGORIES_MAX_LEN, blank=True)

    class Meta:
        model = User
        fields = (
            _FIRST_NAME_FF, _LAST_NAME_FF, _EMAIL_FF, _BIO_FF, _AVATAR_FF
        )
        non_bootstrap_fields = (_BIO_FF, _AVATAR_FF)
        help_texts = {
            _FIRST_NAME_FF: 'User first name.',
            _LAST_NAME_FF: 'User last name.',
            _EMAIL_FF: 'Email address of user.',
            _BIO_FF: 'Biography of user.',
            _AVATAR_FF: 'User avatar',
        }
        error_messages = error_messages(
            model.MODEL_NAME,
            *[ErrorMsgs(field, max_length=True)
              for field in (_FIRST_NAME_FF, _LAST_NAME_FF)]
        )
        widgets = {
            _BIO_FF: SummernoteWidget(),
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
