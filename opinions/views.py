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
from django.urls import reverse
from django.views import View

from soapbox import (
    OPINIONS_APP_NAME, HOME_ROUTE_NAME
)
from utils import app_template_path, redirect_on_success_or_render, \
    is_boolean_true
from categories import STATUS_DRAFT, STATUS_PUBLISHED, CATEGORY_UNASSIGNED
from categories.models import Status, Category
from .forms import OpinionForm
from .models import Opinion
from .constants import OPINION_NEW_ROUTE_NAME, OPINION_ID_ROUTE_NAME


TITLE_NEW = "Creation"
TITLE_UPDATE = "Update"


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
        template_path, context = _render_form(
            OpinionForm(), self.url(), TITLE_NEW)
        return render(request, template_path, context=context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        form = OpinionForm(data=request.POST, files=request.FILES)

        # TODO preview route

        if form.is_valid():
            # save new object
            status, preview = _query_args(request)

            form.instance.user = request.user
            form.instance.status = status
            form.instance.set_slug(form.instance.title)

            form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            template_path, context = None, None
        else:
            template_path, context = _render_form(form, self.url(), TITLE_NEW)
            success = False

        return redirect_on_success_or_render(
            request, success, HOME_ROUTE_NAME, template_path, context)

    def url(self) -> str:
        """
        Get url for opinion creation
        :return: url
        """
        return reverse(OPINION_NEW_ROUTE_NAME)


def _render_form(form: OpinionForm, url: str, title: str,
                 read_only: bool = False,
                 opinion_obj: Opinion = None, status: Status = None) -> tuple[
        str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion template
    :param form: form to display
    :param url: form commit url
    :param title: title
    :param read_only: read only flag, default False
    :param opinion_obj: opinion object, default None
    :param status: status, default None
    :return: tuple of template path and context
    """
    if status is None:
        status = STATUS_DRAFT

    # set initial data
    form[OpinionForm.CATEGORIES_FF].initial = [
        Category.objects.get(name=CATEGORY_UNASSIGNED)
    ] if opinion_obj is None else opinion_obj.categories.all()

    status_text = status if isinstance(status, str) else status.name

    return app_template_path(OPINIONS_APP_NAME, "opinion.html"), {
        "read_only": read_only,
        "form": form,
        "auto_ids": {field: form.auto_id % field for field in form.fields},
        'summernote_fields': [OpinionForm.CONTENT_FF],
        'other_fields': [OpinionForm.TITLE_FF],
        'category_fields': [OpinionForm.CATEGORIES_FF],
        'submit_url': url,
        'title': title,
        'status': status_text,
        'status_bg':
            'bg-primary' if status_text == STATUS_DRAFT else 'bg-success',
    }


def _query_args(request: HttpRequest) -> tuple[Status, bool]:
    """
    Get query arguments from request query
    :param request: http request
    :return: tuple of Status and preview flag
    """
    # query params are in request.GET
    # maybe slightly unorthodox, but saves defining 3 routes
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    status = STATUS_DRAFT
    if 'status' in request.GET:
        if request.GET['status'].lower() == 'publish':
            status = STATUS_PUBLISHED

    status = Status.objects.get(name=status)

    preview = is_boolean_true(request.GET['preview']) \
        if 'preview' in request.GET else False

    return status, preview


class OpinionDetail(LoginRequiredMixin, View):
    """
    Class-based view for individual opinion view/update
    """

    def get(self, request: HttpRequest,
            pk: int, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion
        :param request: http request
        :param pk: id of opinion to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_obj = get_object_or_404(Opinion, id=pk)

        template_path, context = _render_form(
            OpinionForm(instance=opinion_obj),
            self.url(opinion_obj),
            TITLE_UPDATE,
            read_only=opinion_obj and opinion_obj.user.id != request.user.id,
            opinion_obj=opinion_obj,
            status=opinion_obj.status
        )
        return render(request, template_path, context=context)

    def post(self, request: HttpRequest,
             pk: int, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param pk: id of opinion to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_obj = get_object_or_404(Opinion, id=pk)

        if request.user.id != opinion_obj.user.id:
            raise PermissionDenied(
                "Opinions may only be updated by their authors")

        form = OpinionForm(data=request.POST, files=request.FILES,
                           instance=opinion_obj)

        if form.is_valid():
            # normal fields are updated but ManyToMany aren't
            # copy clean data to user object
            opinion_obj.categories.set(
                form.cleaned_data[OpinionForm.CATEGORIES_FF]
            )

            status, preview = _query_args(request)
            opinion_obj.status = status

            # save updated object
            opinion_obj.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            template_path, context = None, None
        else:
            template_path, context = _render_form(
                form,
                self.url(opinion_obj),
                TITLE_UPDATE,
                opinion_obj=opinion_obj,
                status=opinion_obj.status)
            success = False

        return redirect_on_success_or_render(
            request, success, HOME_ROUTE_NAME, template_path, context)

    def url(self, opinion_obj: Opinion) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        return reverse(OPINION_ID_ROUTE_NAME, args=[opinion_obj.id])
