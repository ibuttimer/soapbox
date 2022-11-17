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
from typing import Union, List

from django.http import HttpRequest

from soapbox import CATEGORIES_APP_NAME
from utils import Crud, permission_check
from .models import Category


def category_permissions(request: HttpRequest, context: dict = None) -> dict:
    """
    Get the current user's permissions for Category
    :param request: current request
    :param context: context to update; default None
    :return: dict of permissions with
            `<model_name>_<crud_op>` as key and boolean value
    """
    if context is None:
        context = {}
    model = Category.model_name_lower()
    context.update({
        f'{model}_{op.name.lower()}':
            category_permission_check(request, op, raise_ex=False)
        for op in Crud
    })
    return context


def category_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Category, perm_op,
                            app_label=CATEGORIES_APP_NAME, raise_ex=raise_ex)
