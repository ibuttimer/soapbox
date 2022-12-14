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
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import ResolverMatch, resolve, Resolver404


def redirect_on_success_or_render(request: HttpRequest, success: bool,
                                  redirect_to: str = '/',
                                  *args,
                                  template_path: str = None,
                                  context: dict = None) -> HttpResponse:
    """
    Redirect if success, otherwise render the specified template.
    :param request:         http request
    :param success:         success flag
    :param redirect_to:     a view name that can be resolved by
                            `urls.reverse()` or a URL
    :param args:            optional args for view name, (`urls.reverse()`
                            used to reverse-resolve the name)
    :param template_path:   template to render
    :param context:         context for template
    :return: http response
    """
    response: HttpResponse
    if success:
        # success, redirect
        response = redirect(redirect_to, *args)
    else:
        # render template
        response = render(request, template_path, context=context)
    return response


def resolve_req(
        request: HttpRequest, query: str = None) -> Optional[ResolverMatch]:
    """
    Resolve a request, or a request query parameter
    :param request: http request
    :param query: optional query parameter to resolve
    :return: resolver match or None
    """
    match = None
    path = None
    if query and query in request.GET:
        path = request.GET[query].lower()
    else:
        path = request.path

    if path:
        try:
            match = resolve(path)
        except Resolver404:
            pass    # unable to resolve

    return match
