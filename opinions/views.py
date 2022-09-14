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

from datetime import datetime
from enum import Enum
from http import HTTPStatus
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, \
    JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods

from categories import (
    STATUS_DRAFT, STATUS_PUBLISHED, STATUS_PREVIEW, CATEGORY_UNASSIGNED
)
from categories.models import Status, Category
from soapbox import (
    OPINIONS_APP_NAME, HOME_ROUTE_NAME, GET, PATCH
)
from utils import (
    app_template_path, redirect_on_success_or_render, permission_name, Crud
)
from .constants import (
    OPINION_NEW_ROUTE_NAME, OPINION_ID_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_ROUTE_NAME
)
from .forms import OpinionForm
from .models import Opinion

TITLE_NEW = "Creation"
TITLE_UPDATE = "Update"
TITLE_OPINION = "Opinion"

READ_ONLY = 'read_only'     # read-only mode
OWN_ONLY = 'own_only'       # access to own opinions only


class QueryStatus(Enum):
    """ Enum representing status query params """
    DRAFT = 'draft'
    PUBLISH = 'publish'
    PREVIEW = 'preview'


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
        _permission_check(request, Crud.CREATE)

        template_path, context = _render_form(
            TITLE_NEW, submit_url=self.url(), form=OpinionForm())
        return render(request, template_path, context=context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        _permission_check(request, Crud.CREATE)

        form = OpinionForm(data=request.POST, files=request.FILES)

        # TODO preview route

        if form.is_valid():
            # save new object
            status, query = _query_args(request)

            form.instance.user = request.user
            form.instance.status = status
            form.instance.set_slug(form.instance.title)

            _timestamp_opinion(form.instance)

            form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            template_path, context = None, None
        else:
            template_path, context = _render_form(
                TITLE_NEW, submit_url=self.url(), form=form)
            success = False

        return redirect_on_success_or_render(
            request, success, HOME_ROUTE_NAME,
            template_path=template_path, context=context)

    def url(self) -> str:
        """
        Get url for opinion creation
        :return: url
        """
        return reverse(OPINION_NEW_ROUTE_NAME)


def _render_form(title: str,
                 submit_url: str = None,
                 form: OpinionForm = None, opinion_obj: Opinion = None,
                 read_only: bool = False, status: Status = None) -> tuple[
        str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion template
    :param title: title
    :param submit_url: form commit url
    :param form: form to display, default None
    :param opinion_obj: opinion object, default None
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    context = _context(
        title, submit_url=submit_url, form=form, opinion_obj=opinion_obj,
        read_only=read_only, status=status
    )
    context.update({
        'summernote_fields': [OpinionForm.CONTENT_FF],
        'other_fields': [OpinionForm.TITLE_FF],
        'category_fields': [OpinionForm.CATEGORIES_FF],
    })

    # set initial data
    form[OpinionForm.CATEGORIES_FF].initial = [
        Category.objects.get(name=CATEGORY_UNASSIGNED)
    ] if opinion_obj is None else opinion_obj.categories.all()

    return app_template_path(OPINIONS_APP_NAME, "opinion_form.html"), context


def _context(title: str,
             submit_url: str = None,
             form: OpinionForm = None, opinion_obj: Opinion = None,
             read_only: bool = False, status: Status = None) -> dict:
    """
    Generate the context for the template
    :param title: title
    :param submit_url: form commit url, default None
    :param form: form to display, default None
    :param opinion_obj: opinion object, default None
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    if status is None:
        status = STATUS_DRAFT

    status_text = status if isinstance(status, str) else status.name

    context = {
        'title': title,
        READ_ONLY: read_only,
        'status': status_text,
        'status_bg':
            'bg-primary' if status_text == STATUS_DRAFT else 'bg-success',
    }

    if form is not None:
        context['form'] = form
        context['submit_url'] = submit_url

    if opinion_obj is not None:
        context['opinion'] = opinion_obj

    return context


def _render_view(title: str,
                 opinion_obj: Opinion = None,
                 read_only: bool = False, status: Status = None) -> tuple[
        str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion view
    :param title: title
    :param opinion_obj: opinion object, default None
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    context = _context(
        title, opinion_obj=opinion_obj, read_only=read_only, status=status
    )
    context.update({
        'categories': opinion_obj.categories.all(),
        'is_preview': status.name == STATUS_PREVIEW if status else False
    })

    return app_template_path(OPINIONS_APP_NAME, "opinion_view.html"), context


def _timestamp_opinion(opinion: Opinion):
    """
    Update opinion timestamps
    :param opinion: opinion to update
    """
    timestamp = datetime.now(tz=ZoneInfo("UTC"))
    opinion.updated = timestamp
    if opinion.status == Status.objects.get(name=STATUS_PUBLISHED):
        if opinion.published.year == 1:
            # first time published
            opinion.published = timestamp


def _query_args(request: HttpRequest) -> tuple[Status, QueryStatus]:
    """
    Get query arguments from request query
    :param request: http request
    :return: tuple of Status and QueryStatus
    """
    # query params are in request.GET
    # maybe slightly unorthodox, but saves defining 3 routes
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    status = STATUS_DRAFT
    query = QueryStatus.DRAFT
    if 'status' in request.GET:
        req_status = request.GET['status'].lower()
        for status_name, query_opt in [
            (STATUS_PUBLISHED, QueryStatus.PUBLISH),
            (STATUS_PREVIEW, QueryStatus.PREVIEW)
        ]:
            if req_status == query_opt.name.lower():
                status = status_name
                query = query_opt
                break

    status = Status.objects.get(name=status)

    return status, query


def _permission_check(request: HttpRequest, op: Crud):
    """
    Check request user has specified permission
    :param request: http request
    :param op: Crud operation to check
    """
    if not request.user.has_perm(
            permission_name(Opinion, op, app_label=OPINIONS_APP_NAME)):
        raise PermissionDenied("Insufficient permissions")


def _own_opinion_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check request user is opinion author
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id:
        raise PermissionDenied(
            "Opinions may only be updated by their authors")


def _published_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check requested opinion is published
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id and \
            opinion_obj.status.name != STATUS_PUBLISHED:
        raise PermissionDenied(
            "Opinion unavailable")


class OpinionDetail(LoginRequiredMixin, View):
    """
    Class-based view for individual opinion view/update
    """

    def get(self, request: HttpRequest,
            identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion
        :param request: http request
        :param identifier: id or slug of opinion to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        _permission_check(request, Crud.READ)

        opinion_obj = self._get_opinion(identifier)

        if OWN_ONLY in kwargs and kwargs[OWN_ONLY]:
            # perform own opinion check
            _own_opinion_check(request, opinion_obj)

        # perform published check, other users don't have access to
        # unpublished opinions
        _published_check(request, opinion_obj)

        read_only = opinion_obj and opinion_obj.user.id != request.user.id \
            if READ_ONLY not in kwargs else kwargs[READ_ONLY]
        render_args = {
            READ_ONLY: read_only,
            'opinion_obj': opinion_obj,
            'status': opinion_obj.status
        }
        if read_only:
            renderer = _render_view
        else:
            renderer = _render_form
            render_args.update({
                'submit_url': self.url(opinion_obj),
                'form': OpinionForm(instance=opinion_obj),
            })

        template_path, context = renderer(
            opinion_obj.title if read_only else TITLE_UPDATE,
            **render_args
        )
        return render(request, template_path, context=context)

    def _get_opinion(self, identifier: [int, str]) -> Opinion:
        """
        Get opinion for specified identifier
        :param identifier: id or slug of opinion to get
        :return: opinion
        """
        query = {'id' if isinstance(identifier, int) else 'slug': identifier}
        return get_object_or_404(Opinion, **query)

    def post(self, request: HttpRequest,
             identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param identifier: id or slug of opinion to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        _permission_check(request, Crud.UPDATE)

        opinion_obj = self._get_opinion(identifier)
        success = True                      # default to success
        success_route = HOME_ROUTE_NAME     # on success default route
        success_args = []                   # on success route args

        # perform own opinion check
        _own_opinion_check(request, opinion_obj)

        form = OpinionForm(data=request.POST, files=request.FILES,
                           instance=opinion_obj)

        if form.is_valid():
            # normal fields are updated but ManyToMany aren't
            # copy clean data to user object
            opinion_obj.categories.set(
                form.cleaned_data[OpinionForm.CATEGORIES_FF]
            )

            status, query = _query_args(request)
            opinion_obj.status = status

            _timestamp_opinion(opinion_obj)

            # save updated object
            opinion_obj.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            if query == QueryStatus.PREVIEW:
                # saved show preview
                success_route = OPINION_PREVIEW_ID_ROUTE_NAME
                success_args = [opinion_obj.id]
            # else redirect to home

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
            request, success, success_route, *success_args,
            template_path=template_path, context=context)

    def url(self, opinion_obj: Opinion) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        raise NotImplementedError(
            "'url' method must be overridden by sub classes")


class OpinionDetailById(OpinionDetail):
    """
    Class-based view for individual opinion view/update by id
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
        return OpinionDetail.get(self, request, pk, *args, **kwargs)

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
        return OpinionDetail.post(self, request, pk, *args, **kwargs)

    def url(self, opinion_obj: Opinion) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        return reverse(OPINION_ID_ROUTE_NAME, args=[opinion_obj.id])


class OpinionDetailPreviewById(OpinionDetail):
    """
    Class-based view for individual opinion preview by id
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
        _permission_check(request, Crud.READ)

        # preview is readonly and user can only preview their own opinions
        preview_kwargs = kwargs.copy()
        preview_kwargs[READ_ONLY] = True
        preview_kwargs[OWN_ONLY] = True
        return OpinionDetail.get(self, request, pk, *args, **preview_kwargs)

    def post(self, request: HttpRequest,
             pk: int, *args, **kwargs) -> HttpResponse:
        """
        POST method for Opinion preview not allowed
        :param request: http request
        :param pk: id of opinion to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        # POST not allowed for preview
        return HttpResponseNotAllowed([GET])

    def url(self, opinion_obj: Opinion) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        return reverse(OPINION_PREVIEW_ID_ROUTE_NAME, args=[opinion_obj.id])


class OpinionDetailBySlug(OpinionDetail):
    """
    Class-based view for individual opinion view/update by slug
    """

    def get(self, request: HttpRequest,
            slug: str, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion
        :param request: http request
        :param slug: slug of opinion to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return OpinionDetail.get(self, request, slug, *args, **kwargs)

    def post(self, request: HttpRequest,
             slug: str, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param slug: slug of opinion to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return OpinionDetail.post(self, request, slug, *args, **kwargs)

    def url(self, opinion_obj: Opinion) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        return reverse(OPINION_SLUG_ROUTE_NAME, args=[opinion_obj.slug])


@login_required
@require_http_methods([PATCH])
def opinion_status_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Class-based view for opinion.
    :param request: http request
    :param pk:      id of opinion
    :return:
    """
    _permission_check(request, Crud.UPDATE)

    opinion_obj = get_object_or_404(Opinion, pk=pk)

    _own_opinion_check(request, opinion_obj)

    status, query = _query_args(request)

    opinion_obj.status = status
    opinion_obj.save()

    return JsonResponse({
        'redirect': '/',
        'status': opinion_obj.status.name
    }, status=HTTPStatus.OK)
