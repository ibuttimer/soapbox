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
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from base.constants import FOLLOWING_FEED_ROUTE_NAME, CATEGORY_FEED_ROUTE_NAME
from soapbox import BASE_APP_NAME
from soapbox.constants import (
    HOME_MENU_CTX, HELP_MENU_CTX, HELP_ROUTE_NAME, HOME_ROUTE_NAME
)
from utils import app_template_path, namespaced_url, resolve_req


def get_landing(request: HttpRequest) -> HttpResponse:
    """
    Render landing page
    :param request: request
    :return: response
    """
    return render(request, app_template_path(BASE_APP_NAME, "landing.html")) \
        if not request.user or not request.user.is_authenticated else \
        redirect(namespaced_url(BASE_APP_NAME, FOLLOWING_FEED_ROUTE_NAME))


def get_home(request: HttpRequest) -> HttpResponse:
    """
    Render home page
    :param request: request
    :return: response
    """
    return render(request, app_template_path(BASE_APP_NAME, "home.html")) \
        if request.user and request.user.is_authenticated else \
        get_landing(request)


def get_help(request: HttpRequest) -> HttpResponse:
    """
    Render help page
    :param request: request
    :return: response
    """
    from opinions.help import get_search_terms_help, get_reactions_help

    context = {}
    context.update(get_search_terms_help())
    context.update(get_reactions_help())
    return render(
        request, app_template_path(BASE_APP_NAME, "help.html"),
        context=context
    )


def add_base_context(request: HttpRequest, context: dict = None) -> dict:
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
        for ctx, routes in [
            (HOME_MENU_CTX, [
                HOME_ROUTE_NAME, FOLLOWING_FEED_ROUTE_NAME,
                CATEGORY_FEED_ROUTE_NAME
            ]),
            (HELP_MENU_CTX, [HELP_ROUTE_NAME]),
        ]:
            context[ctx] = called_by.url_name in routes

    return context
