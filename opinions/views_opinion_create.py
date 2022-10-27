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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest, HttpResponse
)
from django.shortcuts import render
from django.views import View

from soapbox import (
    HOME_ROUTE_NAME, OPINIONS_APP_NAME
)
from utils import (
    redirect_on_success_or_render, Crud, reverse_q, namespaced_url
)
from .constants import (
    OPINION_NEW_ROUTE_NAME, SUBMIT_URL_CTX, OPINION_FORM_CTX
)
from .forms import OpinionForm
from .views_utils import (
    opinion_permission_check, opinion_save_query_args, timestamp_content,
    render_opinion_form, generate_excerpt
)

TITLE_NEW = "Creation"


class OpinionCreate(LoginRequiredMixin, View):
    """
    Class-based view for opinion creation
    """
    # https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequired-mixin

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_permission_check(request, Crud.CREATE)

        template_path, context = render_opinion_form(
            TITLE_NEW, **{
                SUBMIT_URL_CTX: self.url(),
                OPINION_FORM_CTX: OpinionForm()
            })
        return render(request, template_path, context=context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_permission_check(request, Crud.CREATE)

        form = OpinionForm(data=request.POST, files=request.FILES)

        # TODO preview route

        if form.is_valid():
            # save new object
            status, query = opinion_save_query_args(request)

            form.instance.user = request.user
            form.instance.status = status
            form.instance.set_slug(form.instance.title)

            form.instance.excerpt = generate_excerpt(form.instance.content)

            timestamp_content(form.instance)

            form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            template_path, context = None, None
        else:
            template_path, context = render_opinion_form(
                TITLE_NEW, **{
                    SUBMIT_URL_CTX: self.url(),
                    OPINION_FORM_CTX: form
                })
            success = False

        return redirect_on_success_or_render(
            request, success, HOME_ROUTE_NAME,
            template_path=template_path, context=context)

    def url(self) -> str:
        """
        Get url for opinion creation
        :return: url
        """
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, OPINION_NEW_ROUTE_NAME)
        )
