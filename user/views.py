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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from soapbox import (
    USER_APP_NAME, HOME_ROUTE_NAME, IMAGE_FILE_TYPES, AVATAR_BLANK_URL
)
from utils import app_template_path, redirect_on_success_or_render
from .forms import UserForm
from .models import User


# https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequired-mixin
class UserDetail(LoginRequiredMixin, View):
    """
    Class-based view for users
    """

    def get(self, request: HttpRequest,
            pk: int, *args, **kwargs) -> HttpResponse:
        """
        GET method for User
        :param request: http request
        :param pk: id of user to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        user_obj = get_object_or_404(User, id=pk)

        template_path, context = self._render_profile(request, user_obj)
        return render(request, template_path, context=context)

    @staticmethod
    def _render_profile(
            request: HttpRequest, user_obj: User) -> tuple[
                str, dict[str, User | list[str] | UserForm | bool]]:
        """
        Render the profile template
        :param request: http request
        :param user_obj: user
        :return: http response
        """
        form = UserForm(instance=user_obj)

        avatar_url = AVATAR_BLANK_URL \
            if User.AVATAR_BLANK in form.initial[UserForm.AVATAR_FF].url \
            else form.initial[UserForm.AVATAR_FF].url

        return app_template_path(USER_APP_NAME, "profile_view.html"), {
            "user_profile": user_obj,
            "read_only": user_obj.id != request.user.id,
            "form": form,
            "auto_ids": {field: form.auto_id % field for field in form.fields},
            'lhs_fields': [
                UserForm.FIRST_NAME_FF, UserForm.LAST_NAME_FF,
                UserForm.EMAIL_FF
            ],
            'summernote_fields': [UserForm.BIO_FF],
            'img_fields': [UserForm.AVATAR_FF],
            'avatar_url': avatar_url,
            'image_file_types': IMAGE_FILE_TYPES
        }

    def post(self, request: HttpRequest,
             pk: int, *args, **kwargs) -> HttpResponse:
        """
        POST method to update User
        :param request: http request
        :param pk: id of user to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        if request.user.id != pk:
            raise PermissionDenied("Users may only update their own profile")

        user_obj = get_object_or_404(User, id=pk)

        form = UserForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # copy clean data to user object
            for field in form.cleaned_data:
                save_data = form.cleaned_data[field]
                if field == UserForm.AVATAR_FF:
                    if not save_data:
                        # user cleared, reset to placeholder
                        save_data = User.AVATAR_BLANK
                setattr(user_obj, field, save_data)
            # save updated object
            user_obj.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            # TODO delete old avatar from cloudinary

            template_path, context = None, None
        else:
            template_path, context = self._render_profile(request, user_obj)
            context['form'] = form
            success = False

        return redirect_on_success_or_render(
            request, success, HOME_ROUTE_NAME, template_path, context)
