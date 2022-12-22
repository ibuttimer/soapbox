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
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from soapbox import (
    USER_APP_NAME, HOME_ROUTE_NAME, IMAGE_FILE_TYPES, AVATAR_BLANK_URL,
    DEVELOPMENT, DEV_IMAGE_FILE_TYPES
)
from soapbox.constants import (
    USER_MENU_CTX, IS_SUPER_CTX, IS_MODERATOR_CTX, IS_AUTHOR_CTX,
    SIGN_IN_MENU_CTX, REGISTER_MENU_CTX, LOGIN_ROUTE_NAME,
    REGISTER_ROUTE_NAME, ACCOUNTS_URL
)
from utils import app_template_path, redirect_on_success_or_render, resolve_req
from . import USER_ID_ROUTE_NAME
from .constants import USER_USERNAME_ROUTE_NAME
from .forms import UserForm
from .models import User
from .queries import is_moderator, is_author, get_social_providers


# https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequired-mixin
class UserDetail(LoginRequiredMixin, View):
    """
    Class-based view for users
    """

    def get(self, request: HttpRequest,
            identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        GET method for User
        :param request: http request
        :param identifier: id or username of user to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        user_obj = self._get_user(identifier)

        template_path, context = self._render_profile(request, user_obj)
        return render(request, template_path, context=context)

    @staticmethod
    def _get_user(identifier: [int, str]) -> User:
        """
        Get user for specified identifier
        :param identifier: id or slug of user to get
        :return: user
        """
        query = {
            User.id_field() if isinstance(identifier, int)
            else User.USERNAME_FIELD: identifier
        }
        return get_object_or_404(User, **query)

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

        # set initial data
        form[UserForm.CATEGORIES_FF].initial = list(user_obj.categories.all())
        if request.user.is_superuser:
            # groups only displayed when superuser looking
            form[UserForm.GROUPS_FF].initial = list(user_obj.groups.all())

        # avatar to display
        avatar_url = AVATAR_BLANK_URL \
            if User.AVATAR_BLANK in form.initial[UserForm.AVATAR_FF].url \
            else form.initial[UserForm.AVATAR_FF].url

        read_only = user_obj.id != request.user.id

        return app_template_path(USER_APP_NAME, "profile.html"), {
            "user_profile": user_obj,
            "read_only": read_only and not request.user.is_superuser,
            "form": form,
            'lhs_fields': [
                UserForm.FIRST_NAME_FF, UserForm.LAST_NAME_FF,
                UserForm.EMAIL_FF
            ],
            'avatar_url': avatar_url,
            'image_file_types':
                # not all image types supported by Pillow which is used by
                # ImageField in dev mode
                DEV_IMAGE_FILE_TYPES if DEVELOPMENT else IMAGE_FILE_TYPES
        }

    def post(self, request: HttpRequest,
             identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        POST method to update User
        :param request: http request
        :param identifier: id or username of user to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        user_obj = self._get_user(identifier)

        if request.user.id != user_obj.id and not request.user.is_superuser:
            raise PermissionDenied("Users may only update their own profile")

        form = UserForm(data=request.POST, files=request.FILES,
                        instance=user_obj)

        if form.is_valid():
            # normal fields are updated but ManyToMany aren't
            # copy clean data to user object
            user_obj.categories.set(
                form.cleaned_data[UserForm.CATEGORIES_FF]
            )
            if request.user.is_superuser:
                # groups only updated when superuser looking
                user_obj.groups.set(
                    form.cleaned_data[UserForm.GROUPS_FF]
                )
            # special handing for avatar
            save_data = form.cleaned_data[UserForm.AVATAR_FF]
            if save_data is not None:
                if not save_data:   # False for clear
                    # user cleared, reset to placeholder
                    save_data = User.AVATAR_BLANK
                setattr(user_obj, UserForm.AVATAR_FF, save_data)

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
            request, success, HOME_ROUTE_NAME,
            template_path=template_path, context=context)


class UserDetailById(UserDetail):
    """
    Class-based view for users by id
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
        return super().get(request, pk, *args, **kwargs)

    def post(self, request: HttpRequest,
             pk: int, *args, **kwargs) -> HttpResponse:
        """
        POST method to update User
        :param request: http request
        :param pk: id of user to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().post(request, pk, *args, **kwargs)


class UserDetailByUsername(UserDetail):
    """
    Class-based view for users by username
    """

    def get(self, request: HttpRequest,
            name: str, *args, **kwargs) -> HttpResponse:
        """
        GET method for User
        :param request: http request
        :param name: username of user to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().get(request, name, *args, **kwargs)

    def post(self, request: HttpRequest,
             name: str, *args, **kwargs) -> HttpResponse:
        """
        POST method to update User
        :param request: http request
        :param name: username of user to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().post(request, name, *args, **kwargs)


# regex to match socials; e.g. '/accounts/twitter/login/'
SOCIAL_REGEX = re.compile(
    rf'^/{ACCOUNTS_URL}(.*)/login/', re.IGNORECASE)


def _sign_in_route_check(request: HttpRequest, route: str):
    """ Check if sign in route """
    sign_in = route == LOGIN_ROUTE_NAME
    if not sign_in:
        # check socials
        match = SOCIAL_REGEX.match(request.path)
        if match:
            sign_in = match.group(1) in get_social_providers()

    return sign_in


def add_user_context(request: HttpRequest, context: dict = None) -> dict:
    """
    Add base-specific context entries
    :param request: current request
    :param context: context to update; default None
    :return: updated context
    """
    if context is None:
        context = {}
    called_by = resolve_req(request)
    if called_by:
        for ctx, check_func in [
            (USER_MENU_CTX, lambda name: name in [
                USER_ID_ROUTE_NAME, USER_USERNAME_ROUTE_NAME
            ]),
            (SIGN_IN_MENU_CTX,
             lambda name: _sign_in_route_check(request, name)),
            (REGISTER_MENU_CTX, lambda name: name == REGISTER_ROUTE_NAME),
        ]:
            context[ctx] = check_func(called_by.url_name)

    context.update({
        IS_SUPER_CTX: request.user.is_superuser,
        IS_MODERATOR_CTX: is_moderator(request.user),
        IS_AUTHOR_CTX: is_author(request.user),
    })

    return context
