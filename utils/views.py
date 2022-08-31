
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

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect


def redirect_on_success_or_render(request: HttpRequest, success: bool,
                                  redirect_to: str = '/',
                                  template_path: str = None,
                                  context: dict = None) -> HttpResponse:
    """
    Redirect if success, otherwise render the specified template.
    :param request:         http request
    :param success:         success flag
    :param redirect_to:     a view name that can be resolved by
                            `urls.reverse()` or a URL
    :param template_path:   template to render
    :param context:         context for template
    :return: http response
    """
    response: HttpResponse
    if success:
        # success, redirect
        response = redirect(redirect_to)
    else:
        # render template
        response = render(request, template_path, context=context)
    return response
