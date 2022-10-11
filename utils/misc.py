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
import random
import string
import environ
from enum import Enum

from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpRequest
from django.urls import reverse as django_reverse


def append_slash(url: str) -> str:
    """
    Append a slash to the specified url if necessary.
    (See
    https://docs.djangoproject.com/en/4.1/misc/design-philosophies/#definitive-urls)
    :param url: url string
    :return: url string
    """
    result: str = url
    if result[-1] != '/':
        result = f"{url}/"
    return result


def namespaced_url(*args: str) -> str:
    """
    Concatenate supplied arguments into a namespaced URL.
    See https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces
    :param args: elements of url
    :return: url string
    """
    return ":".join(args)


def app_template_path(app: str, *args: str) -> str:
    """
    Concatenate supplied arguments into a relative path to a template file
    :param app: name of app
    :param args: elements of path
    :return: path string
    """
    path = [app]
    path.extend(args)
    return "/".join(path)


def url_path(*args: str) -> str:
    """
    Concatenate arguments into a url path
    :param args: elements of path
    :return: path string
    """
    return "".join([append_slash(segment) for segment in args])


def reverse_q(viewname, urlconf=None, args=None, kwargs=None,
              current_app=None, query_kwargs: dict = None) -> str:
    """
    Wrapper to add query argument support to django's standard `reverse`
    :param viewname:  URL pattern name or the callable view object
    :param urlconf:
            URLconf module containing the URL patterns to use for reversing
    :param args: arguments for url
    :param kwargs: keyword args
    :param current_app: application to which the view belongs
    :param query_kwargs: query arguments
    :return: str
    """
    url = django_reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs,
                         current_app=current_app)
    if query_kwargs:
        url = f'{url}?{"&".join([f"{k}={v}" for k,v in query_kwargs.items()])}'
    return url


def random_string_generator(
        size=10, chars=string.ascii_letters + string.digits):
    """
    Generate a random string.
    Based on code from https://stackoverflow.com/a/58853028/4054609
    :param size: size of string to generate
    :param chars: characters to generate string from
    :return: string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def is_boolean_true(text: str) -> bool:
    """
    Check if `text` represents a boolean True value
    :param text: string to check
    :return: True if represents a boolean True value, otherwise False
    """
    return text.lower() in environ.Env.BOOLEAN_TRUE_STRINGS


class Crud(Enum):
    """
    Enum to map standard CRUD terms to Django models default permissions
    """
    CREATE = 'add'
    READ = 'view'
    UPDATE = 'change'
    DELETE = 'delete'


def permission_name(
        model: [str, models.Model], op: Crud, app_label: str = None) -> str:
    """
    Generate a permission name.
    See
    https://docs.djangoproject.com/en/4.1/topics/auth/default/#default-permissions
    :param model: model or model name
    :param op: CRUD operation
    :param app_label:
        app label for models defined outside of an application in
        INSTALLED_APPS, default none
    :return: permission string
    """
    perm = f'{app_label}.' if app_label else ''
    if not isinstance(model, str):
        model = model._meta.model_name
    return f'{perm}{op.value}_{model}'


def permission_check(
        request: HttpRequest, model: [str, models.Model], op: Crud,
        app_label: str = None, raise_ex: bool = False) -> bool:
    """
    Check request user has specified permission
    :param request: http request
    :param model: model or model name
    :param op: Crud operation to check
    :param app_label:
        app label for models defined outside of an application in
        INSTALLED_APPS, default none
    :param raise_ex: raise exception; default False
    :return: True is has permission
    :raises PermissionDenied if does not have permission and `raise_ex` is
            True
    """
    has_perm = request.user.has_perm(
        permission_name(model, op, app_label=app_label))
    if not has_perm and raise_ex:
        raise PermissionDenied("Insufficient permissions")
    return has_perm
