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
from typing import Optional, Union, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model
from django.http import (
    HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse
)
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_http_methods

from categories import (
    STATUS_PREVIEW, STATUS_PENDING_REVIEW
)
from categories.models import Status
from opinions.comment_data import get_comment_query_args
from opinions.contexts.comment import comments_list_context_for_opinion
from soapbox import (
    OPINIONS_APP_NAME, HOME_ROUTE_NAME, GET, PATCH, HOME_URL, POST
)
from utils import (
    app_template_path, redirect_on_success_or_render, Crud, reverse_q,
    namespaced_url
)
from opinions.constants import (
    OPINION_ID_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_ROUTE_NAME, TEMPLATE_TARGET_ID,
    TEMPLATE_TARGET_TYPE, TEMPLATE_REACTIONS, TEMPLATE_REACTION_CTRLS,
    TEMPLATE_COMMENT_REACTIONS, TEMPLATE_OPINION_REACTIONS,
    SUBMIT_URL_CTX,
    COMMENT_FORM_CTX, READ_ONLY_CTX, USER_CTX, OPINION_CTX,
    STATUS_CTX, OPINION_FORM_CTX, REPORT_FORM_CTX, IS_PREVIEW_CTX,
    ALL_FIELDS, VIEW_OK_CTX, UNDER_REVIEW_TITLE, UNDER_REVIEW_EXCERPT,
    UNDER_REVIEW_TITLE_CTX, UNDER_REVIEW_EXCERPT_CTX, UNDER_REVIEW_CONTENT_CTX,
    UNDER_REVIEW_OPINION_CONTENT, TEMPLATE_TARGET_SLUG, TEMPLATE_TARGET_AUTHOR,
    REDIRECT_CTX, ELEMENT_ID_CTX, HTML_CTX, OPINIONS_ROUTE_NAME, AUTHOR_QUERY,
    STATUS_QUERY
)
from opinions.forms import OpinionForm, CommentForm, ReviewForm
from opinions.models import (
    Opinion, Comment, AgreementStatus, HideStatus, PinStatus, Review,
    FollowStatus
)
from opinions.queries import content_status_check, effective_content_status
from opinions.reactions import (
    OPINION_REACTIONS, COMMENT_REACTIONS, get_reaction_status
)
from opinions.templatetags.reaction_ul_id import reaction_ul_id
from opinions.views.utils import (
    opinion_permission_check, opinion_save_query_args, timestamp_content,
    own_content_check, published_check, get_opinion_context,
    render_opinion_form, comment_permission_check, like_query_args,
    hide_query_args, pin_query_args, generate_excerpt, follow_query_args
)
from opinions.enums import QueryStatus, ReactionStatus

TITLE_NEW = "Creation"
TITLE_UPDATE = "Update"
TITLE_OPINION = "Opinion"

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

        # perform own opinion check
        is_own = own_content_check(
            request, opinion_obj, raise_ex=kwargs.get(OWN_ONLY, False))

        # perform published check, other users don't have access to
        # unpublished opinions
        published_check(request, opinion_obj)

        # read only if not current user's opinion
        read_only = not is_own \
            if READ_ONLY_CTX not in kwargs else kwargs[READ_ONLY_CTX]
        is_preview = opinion_obj.status.name == STATUS_PREVIEW

        # ok to view check
        content_status = content_status_check(
            opinion_obj, current_user=request.user)
        # users can always view their own opinions
        view_ok = is_own \
            if not content_status.view_ok else content_status.view_ok

        render_args = {
            READ_ONLY_CTX: read_only,
            VIEW_OK_CTX: view_ok,
            OPINION_CTX: opinion_obj,
            STATUS_CTX: effective_content_status(opinion_obj),
            IS_PREVIEW_CTX: is_preview,
        }

        if view_ok and comment_permission_check(
                request, Crud.READ, raise_ex=False):
            # get first page comments for opinion
            comments_list_context_for_opinion(
                get_comment_query_args(opinion=opinion_obj),
                request.user, context=render_args
            )

        if read_only:
            # viewing opinion
            renderer = _render_view
            render_args.update({
                USER_CTX: request.user,
            })
            render_args.update({
                # visible opinion which may have not visible
                # under review comments
                COMMENT_FORM_CTX: CommentForm(),
                REPORT_FORM_CTX: ReviewForm(),
            } if view_ok else {
                # not visible under review opinion
                UNDER_REVIEW_TITLE_CTX: UNDER_REVIEW_TITLE,
                UNDER_REVIEW_EXCERPT_CTX: UNDER_REVIEW_EXCERPT,
                UNDER_REVIEW_CONTENT_CTX: UNDER_REVIEW_OPINION_CONTENT,
            })
        else:
            # updating opinion
            renderer = render_opinion_form
            render_args.update({
                SUBMIT_URL_CTX: self.url(opinion_obj),
                OPINION_FORM_CTX: OpinionForm(instance=opinion_obj),
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
        query = {
            Opinion.id_field() if isinstance(identifier, int)
            else Opinion.SLUG_FIELD: identifier
        }
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
        own_content_check(request, opinion_obj)

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

            opinion_obj.excerpt = generate_excerpt(opinion_obj.content)

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
                TITLE_UPDATE, **{
                    SUBMIT_URL_CTX: self.url(opinion_obj),
                    OPINION_FORM_CTX: form,
                    OPINION_CTX: opinion_obj,
                    STATUS_CTX: opinion_obj.status
                })
            success = False

        return redirect_on_success_or_render(
            request, success, success_route, *success_args,
            template_path=template_path, context=context)

    def delete(self, request: HttpRequest,
               identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Opinion
        :param request: http request
        :param identifier: id or slug of opinion to delete
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_permission_check(request, Crud.DELETE)

        opinion_obj = self._get_opinion(identifier)

        # perform own opinion check
        own_content_check(request, opinion_obj, raise_ex=True)

        count, _ = opinion_obj.delete()

        return JsonResponse({
            ELEMENT_ID_CTX: "id--opinion-delete-modal-body",
            HTML_CTX: render_to_string(
                app_template_path(
                    OPINIONS_APP_NAME, "snippet", "content_delete.html"),
                context={
                    # reactions template
                    STATUS_CTX: count > 0,
                },
                request=request),
            REDIRECT_CTX: reverse_q(
                namespaced_url(
                    OPINIONS_APP_NAME, OPINIONS_ROUTE_NAME), query_kwargs={
                        AUTHOR_QUERY: request.user.username,
                        STATUS_QUERY: QueryStatus.ALL.arg
                    })
        }, status=HTTPStatus.OK if count > 0 else HTTPStatus.BAD_REQUEST)

    def url(self, opinion_obj: Opinion) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        raise NotImplementedError(
            "'url' method must be overridden by sub classes")


def _render_view(title: str, **kwargs) -> tuple[
        str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion view
    :param title: title
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = get_opinion_context(title, **kwargs)

    # get reaction controls for opinion & comments
    user = kwargs.get(USER_CTX, None)
    opinion = kwargs.get(OPINION_CTX, None)
    is_preview = kwargs.get(IS_PREVIEW_CTX, False)
    reaction_ctrls = kwargs.get(TEMPLATE_REACTION_CTRLS, {})

    # reaction controls for opinion
    reaction_ctrls.update(
        get_reaction_status(
            user, opinion,
            # no reactions for opinion preview
            enablers={ALL_FIELDS: False} if is_preview else None
        )
    )

    context.update({
        'categories': opinion.categories.all(),
        TEMPLATE_OPINION_REACTIONS: OPINION_REACTIONS,
        TEMPLATE_COMMENT_REACTIONS: COMMENT_REACTIONS,
        TEMPLATE_REACTION_CTRLS: reaction_ctrls,
    })

    return app_template_path(OPINIONS_APP_NAME, "opinion_view.html"), context


class OpinionDetailById(OpinionDetail):
    """
    Class-based view for individual opinion view/update/delete by id
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
        return super().get(request, pk, *args, **kwargs)

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
        return super().post(request, pk, *args, **kwargs)

    def delete(self, request: HttpRequest,
               pk: int, *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Opinion
        :param request: http request
        :param pk: id of opinion to delete
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().delete(request, pk, *args, **kwargs)

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
        preview_kwargs[READ_ONLY_CTX] = True
        preview_kwargs[OWN_ONLY] = True
        return super().get(request, pk, *args, **preview_kwargs)

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

    def delete(self, request: HttpRequest,
               pk: int, *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Opinion
        :param request: http request
        :param pk: id of opinion to delete
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        # DELETE not allowed for preview
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
    Class-based view for individual opinion view/update/delete by slug
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
        return super().get(request, slug, *args, **kwargs)

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
        return super().post(request, slug, *args, **kwargs)

    def delete(self, request: HttpRequest,
               slug: str, *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Opinion
        :param request: http request
        :param slug: slug of opinion to delete
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().delete(request, slug, *args, **kwargs)

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

    own_content_check(request, opinion_obj)

    status, _ = opinion_save_query_args(request)

    opinion_obj.status = status
    opinion_obj.save()

    return redirect_response(HOME_URL, extra={
        STATUS_CTX: opinion_obj.status.name
    })


def redirect_response(url: str, extra: Optional[dict] = None,
                      status: HTTPStatus = HTTPStatus.OK) -> HttpResponse:
    """
    Generate redirect response.
    :param url: url to redirect to
    :param extra: extra payload content; default None
    :param status: http status code; default HTTPStatus.OK
    :return: response
    """
    payload = {
        REDIRECT_CTX: url
    }
    if isinstance(extra, dict):
        payload.update(extra)

    return JsonResponse(payload, status=status)


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

    return like_patch(request, Opinion, pk)


def like_patch(
        request: HttpRequest, model: Type[Model], pk: int) -> HttpResponse:
    """
    View function to update content like status.
    :param request: http request
    :param model:   content model class
    :param pk:      id of opinion
    :return: http response
    """
    content = get_object_or_404(model, pk=pk)

    status, reaction = like_query_args(request)

    code = HTTPStatus.BAD_REQUEST
    if reaction in [ReactionStatus.AGREE, ReactionStatus.DISAGREE]:
        query_args = {
            AgreementStatus.content_field(content): content,
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

    return react_response(request, content, code)


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

    reaction = pin_query_args(request)

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

    return react_response(request, opinion_obj, code)


@login_required
@require_http_methods([POST])
def opinion_report_post(request: HttpRequest, pk: int) -> JsonResponse:
    """
    View function to update opinion report status.
    :param request: http request
    :param pk:      id of opinion
    :return: http response
    """
    opinion_permission_check(request, Crud.READ)

    return report_post(request, Opinion, pk)


def report_post(
        request: HttpRequest, model: Type[Model], pk: int) -> JsonResponse:
    """
    View function to update content report status.
    :param request: http request
    :param model:   content model class
    :param pk:      id of opinion
    :return: http response
    """
    content = get_object_or_404(model, pk=pk)

    form = ReviewForm(data=request.POST)

    if form.is_valid():
        # save new object
        setattr(form.instance, Review.content_field(content), content)
        form.instance.requested = request.user
        form.instance.status = Status.objects.get(name=STATUS_PENDING_REVIEW)

        timestamp_content(form.instance)

        form.save()
        # django autocommits changes
        # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

        response = react_response(request, content, HTTPStatus.OK)

    else:
        # display form errors
        response = JsonResponse({
            HTML_CTX: render_to_string(
                app_template_path(
                    "snippet", "form_errors.html"),
                context={
                    'form': form,
                },
                request=request),
        }, status=HTTPStatus.BAD_REQUEST)

    return response


def react_response(
    request: HttpRequest, content: Union[Opinion, Comment],
    code: Union[HTTPStatus, int]
) -> JsonResponse:
    """
    Generate reactions element response to a reaction update.
    :param request: http request
    :param content: opinion or comment
    :param code: status code for response
    :return: response
    """
    # Note: if code is HTTPStatus.NO_CONTENT nothing is returned in response
    reaction_ctrls = get_reaction_status(request.user, content)

    target_type = content.model_name_lower()

    # TODO after follow/unfollow reflect status in all elements by author
    # not just the one clicked

    return JsonResponse({
        ELEMENT_ID_CTX: reaction_ul_id(target_type, content.id),
        HTML_CTX: render_to_string(
            app_template_path(
                OPINIONS_APP_NAME, "snippet", "reactions.html"),
            context={
                # reactions template
                TEMPLATE_TARGET_ID: content.id,
                TEMPLATE_TARGET_SLUG: content.slug,
                TEMPLATE_TARGET_AUTHOR: content.user.id,
                TEMPLATE_TARGET_TYPE: target_type,
                TEMPLATE_REACTIONS: OPINION_REACTIONS
                if isinstance(content, Opinion) else COMMENT_REACTIONS,
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

    return hide_patch(request, Opinion, pk)


def hide_patch(
        request: HttpRequest, model: Type[Model], pk: int) -> HttpResponse:
    """
    View function to update opinion hide status.
    :param request: http request
    :param model:   content model class
    :param pk:      id of opinion
    :return:
    """
    content = get_object_or_404(model, pk=pk)

    reaction = hide_query_args(request)

    code = HTTPStatus.BAD_REQUEST
    if reaction in [ReactionStatus.HIDE, ReactionStatus.SHOW]:
        query_args = {
            HideStatus.content_field(content): content,
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

    return redirect_response(HOME_URL, extra={
            STATUS_CTX: reaction.arg
        }, status=code)


@login_required
@require_http_methods([PATCH])
def opinion_follow_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update follow opinion author status.
    :param request: http request
    :param pk:      id of content
    :return: http response
    """
    opinion_permission_check(request, Crud.READ)

    return follow_patch(request, Opinion, pk)


def follow_patch(
        request: HttpRequest, model: Type[Model], pk: int) -> HttpResponse:
    """
    View function to update follow content author status.
    :param request: http request
    :param model:   content model class
    :param pk:      id of content
    :return: http response
    """
    content = get_object_or_404(model, pk=pk)

    reaction = follow_query_args(request)

    code = HTTPStatus.BAD_REQUEST
    if reaction in [ReactionStatus.FOLLOW, ReactionStatus.UNFOLLOW]:
        query_args = {
            FollowStatus.AUTHOR_FIELD: content.user,
            FollowStatus.USER_FIELD: request.user
        }
        query = FollowStatus.objects.filter(**query_args)

        code = HTTPStatus.NO_CONTENT
        if query.exists() and reaction == ReactionStatus.UNFOLLOW:
            # remove follow record if exists, otherwise no change
            deleted, _ = query.delete()
            if deleted:
                code = HTTPStatus.OK
        elif reaction == ReactionStatus.FOLLOW:
            obj, created = FollowStatus.objects.get_or_create(**query_args)
            if created:
                code = HTTPStatus.OK

    return react_response(request, content, code)
