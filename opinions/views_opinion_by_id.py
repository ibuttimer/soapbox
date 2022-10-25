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
from http import HTTPStatus
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse
)
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_http_methods

from categories import (
    STATUS_PREVIEW
)
from categories.models import Status
from opinions.constants import (
    OPINION_ID_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_ROUTE_NAME, OPINION_ID_QUERY, PAGE_QUERY,
    PER_PAGE_QUERY, COMMENT_DEPTH_QUERY, PARENT_ID_QUERY, TEMPLATE_TARGET_ID,
    TEMPLATE_TARGET_TYPE, TEMPLATE_REACTIONS, TEMPLATE_REACTION_CTRLS,
    TEMPLATE_COMMENT_REACTIONS, TEMPLATE_OPINION_REACTIONS
)
from soapbox import (
    OPINIONS_APP_NAME, HOME_ROUTE_NAME, GET, PATCH, HOME_URL
)
from user.models import User
from utils import (
    app_template_path, redirect_on_success_or_render, Crud, reverse_q,
    namespaced_url
)
from .comment_data import get_comment_bundle
from .forms import OpinionForm, CommentForm
from .models import Opinion, Comment, AgreementStatus, HideStatus, PinStatus
from .reactions import (
    OPINION_REACTIONS, COMMENT_REACTIONS, get_reaction_status
)
from .templatetags.reaction_ul_id import reaction_ul_id
from .views_utils import (
    opinion_permission_check, opinion_save_query_args, timestamp_content,
    own_opinion_check, published_check, get_opinion_context,
    render_opinion_form, comment_permission_check, DEFAULT_COMMENT_DEPTH,
    opinion_like_query_args, opinion_hide_query_args, opinion_pin_query_args
)
from .enums import QueryArg, QueryStatus, ReactionStatus, PerPage

TITLE_NEW = "Creation"
TITLE_UPDATE = "Update"
TITLE_OPINION = "Opinion"

READ_ONLY = 'read_only'     # read-only mode
OWN_ONLY = 'own_only'       # access to own opinions only


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
        opinion_permission_check(request, Crud.READ)

        opinion_obj = self._get_opinion(identifier)

        if OWN_ONLY in kwargs and kwargs[OWN_ONLY]:
            # perform own opinion check
            own_opinion_check(request, opinion_obj)

        # perform published check, other users don't have access to
        # unpublished opinions
        published_check(request, opinion_obj)

        comments = get_comment_bundle({
            q: QueryArg(v, True) for q, v in [
                (OPINION_ID_QUERY, opinion_obj.id),
                (PARENT_ID_QUERY, Comment.NO_PARENT),
                (PAGE_QUERY, 1),
                (PER_PAGE_QUERY, PerPage.SIX),
                (COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH)
            ]
        }, request.user) if \
            comment_permission_check(request, Crud.READ, raise_ex=False) \
            else []

        read_only = opinion_obj and opinion_obj.user.id != request.user.id \
            if READ_ONLY not in kwargs else kwargs[READ_ONLY]
        render_args = {
            READ_ONLY: read_only,
            'opinion_obj': opinion_obj,
            'status': opinion_obj.status
        }
        if read_only:
            renderer = _render_view
            render_args.update({
                'form': CommentForm(),
                'comments': comments,
                'user': request.user,
            })
        else:
            renderer = render_opinion_form
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
        opinion_permission_check(request, Crud.UPDATE)

        opinion_obj = self._get_opinion(identifier)
        success = True                      # default to success
        success_route = HOME_ROUTE_NAME     # on success default route
        success_args = []                   # on success route args

        # perform own opinion check
        own_opinion_check(request, opinion_obj)

        form = OpinionForm(data=request.POST, files=request.FILES,
                           instance=opinion_obj)

        if form.is_valid():
            # normal fields are updated but ManyToMany aren't
            # copy clean data to user object
            opinion_obj.categories.set(
                form.cleaned_data[OpinionForm.CATEGORIES_FF]
            )

            status, query = opinion_save_query_args(request)
            opinion_obj.status = status

            timestamp_content(opinion_obj)

            # save updated object
            opinion_obj.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            if query == QueryStatus.PREVIEW:
                # saved show preview
                success_route = namespaced_url(
                    OPINIONS_APP_NAME, OPINION_PREVIEW_ID_ROUTE_NAME)
                success_args = [opinion_obj.id]
            # else redirect to home

            template_path, context = None, None
        else:
            template_path, context = render_opinion_form(
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


def _render_view(title: str,
                 submit_url: str = None,
                 form: OpinionForm = None,
                 opinion_obj: Opinion = None,
                 comments: dict = None,
                 user: User = None,
                 read_only: bool = False, status: Status = None) -> tuple[
        str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion view
    :param title: title
    :param opinion_obj: opinion object, default None
    :param comments: details of comments
    :param user: current user
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    context = get_opinion_context(
        title, submit_url=submit_url, form=form, opinion_obj=opinion_obj,
        comments=comments, read_only=read_only, status=status
    )

    # get reaction controls for opinion & comments
    reaction_ctrls = get_reaction_status(user, opinion_obj)
    reaction_ctrls.update(
        get_reaction_status(user, comments))

    context.update({
        'categories': opinion_obj.categories.all(),
        'is_preview': status.name == STATUS_PREVIEW if status else False,
        TEMPLATE_OPINION_REACTIONS: OPINION_REACTIONS,
        TEMPLATE_COMMENT_REACTIONS: COMMENT_REACTIONS,
        TEMPLATE_REACTION_CTRLS: reaction_ctrls,
    })

    return app_template_path(OPINIONS_APP_NAME, "opinion_view.html"), context


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
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
            args=[opinion_obj.id])


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
        opinion_permission_check(request, Crud.READ)

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
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, OPINION_PREVIEW_ID_ROUTE_NAME),
            args=[opinion_obj.id])


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
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, OPINION_SLUG_ROUTE_NAME),
            args=[opinion_obj.slug])


@login_required
@require_http_methods([PATCH])
def opinion_status_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update opinion status.
    :param request: http request
    :param pk:      id of opinion
    :return: response
    """
    opinion_permission_check(request, Crud.UPDATE)

    opinion_obj = get_object_or_404(Opinion, pk=pk)

    own_opinion_check(request, opinion_obj)

    status, query = opinion_save_query_args(request)

    opinion_obj.status = status
    opinion_obj.save()

    return redirect_response(HOME_URL, extra={
        'status': opinion_obj.status.name
    })


def redirect_response(url: str, extra: Optional[dict] = None) -> HttpResponse:
    """
    Generate redirect response.
    :param url: url to redirect to
    :param extra: extra payload content; default None
    :return: response
    """
    payload = {
        'redirect': url
    }
    if isinstance(extra, dict):
        payload.update(extra)

    return JsonResponse(payload, status=HTTPStatus.OK)


@login_required
@require_http_methods([PATCH])
def opinion_like_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update opinion like status.
    :param request: http request
    :param pk:      id of opinion
    :return: http response
    """
    opinion_permission_check(request, Crud.READ)

    opinion_obj = get_object_or_404(Opinion, pk=pk)

    status, reaction = opinion_like_query_args(request)

    code = HTTPStatus.BAD_REQUEST
    if reaction in [ReactionStatus.AGREE, ReactionStatus.DISAGREE]:
        query_args = {
            AgreementStatus.OPINION_FIELD: opinion_obj,
            AgreementStatus.USER_FIELD: request.user
        }
        query = AgreementStatus.objects.filter(**query_args)

        code = HTTPStatus.NO_CONTENT
        if query.exists():
            agreement = query.first()
            if agreement.status != status:
                # change status
                agreement.status = status
                agreement.save()
                code = HTTPStatus.OK
            else:
                # toggle status
                deleted, _ = query.delete()
                if deleted:
                    code = HTTPStatus.OK
        else:
            query_args.update({
                AgreementStatus.STATUS_FIELD: status
            })
            agreement = AgreementStatus.objects.create(**query_args)
            if agreement is not None:
                code = HTTPStatus.OK

    return opinion_react_response(request, opinion_obj, code)


@login_required
@require_http_methods([PATCH])
def opinion_pin_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update opinion pin status.
    :param request: http request
    :param pk:      id of opinion
    :return: http response
    """
    opinion_permission_check(request, Crud.READ)

    opinion_obj = get_object_or_404(Opinion, pk=pk)

    status, reaction = opinion_pin_query_args(request)

    code = HTTPStatus.BAD_REQUEST
    if reaction in [ReactionStatus.PIN, ReactionStatus.UNPIN]:
        query_args = {
            PinStatus.OPINION_FIELD: opinion_obj,
            PinStatus.USER_FIELD: request.user
        }
        query = PinStatus.objects.filter(**query_args)

        code = HTTPStatus.NO_CONTENT
        if query.exists() and reaction == ReactionStatus.UNPIN:
            deleted, _ = query.delete()
            if deleted:
                code = HTTPStatus.OK
        elif reaction == ReactionStatus.PIN:
            _, created = PinStatus.objects.get_or_create(**query_args)
            if created:
                code = HTTPStatus.OK

    return opinion_react_response(request, opinion_obj, code)


def opinion_react_response(
            request: HttpRequest, opinion_obj: Opinion, code: HTTPStatus
        ) -> HttpResponse:
    """
    View function to update opinion like status.
    :param request: http request
    :param opinion_obj: opinion
    :param code: status code for response
    :return: response
    """
    # Note: if code is HTTPStatus.NO_CONTENT nothing is returned in response
    reaction_ctrls = get_reaction_status(request.user, opinion_obj)

    return JsonResponse({
        'element_id': reaction_ul_id('opinion', opinion_obj.id),
        'html': render_to_string(
            app_template_path(
                OPINIONS_APP_NAME, "snippet", "reactions.html"),
            context={
                # reactions template
                TEMPLATE_TARGET_ID: opinion_obj.id,
                TEMPLATE_TARGET_TYPE: 'opinion',
                TEMPLATE_REACTIONS: OPINION_REACTIONS,
                TEMPLATE_REACTION_CTRLS: reaction_ctrls,
            },
            request=request)
    }, status=code)


@login_required
@require_http_methods([PATCH])
def opinion_hide_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update opinion hide status.
    :param request: http request
    :param pk:      id of opinion
    :return:
    """
    opinion_permission_check(request, Crud.READ)

    opinion_obj = get_object_or_404(Opinion, pk=pk)

    status, reaction = opinion_hide_query_args(request)

    code = HTTPStatus.BAD_REQUEST
    if reaction in [ReactionStatus.HIDE, ReactionStatus.SHOW]:
        query_args = {
            HideStatus.OPINION_FIELD: opinion_obj,
            HideStatus.USER_FIELD: request.user
        }
        query = HideStatus.objects.filter(**query_args)

        code = HTTPStatus.NO_CONTENT
        if query.exists() and reaction == ReactionStatus.SHOW:
            # remove hide record if exists, otherwise no change
            deleted, _ = query.delete()
            if deleted:
                code = HTTPStatus.OK
        elif reaction == ReactionStatus.HIDE:
            obj, created = HideStatus.objects.get_or_create(**query_args)
            if created:
                code = HTTPStatus.OK

    return redirect_response(HOME_URL)
