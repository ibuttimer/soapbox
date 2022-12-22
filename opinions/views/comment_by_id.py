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
import json
from enum import Enum
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest, HttpResponse, JsonResponse
)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_http_methods

from categories.constants import STATUS_DELETED, STATUS_PREVIEW
from categories.models import Status
from opinions.comment_data import (
    get_comment_query_args, CommentData, get_comments_review_status
)
from opinions.constants import (
    STATUS_CTX, VIEW_OK_CTX, COMMENT_CTX, TEMPLATE_REACTION_CTRLS, USER_CTX,
    TEMPLATE_COMMENT_REACTIONS, COMMENT_ID_ROUTE_NAME,
    COMMENT_SLUG_ROUTE_NAME, OPINION_CTX, COMMENT_FORM_CTX, REPORT_FORM_CTX,
    ELEMENT_ID_CTX, HTML_CTX, REFERENCE_QUERY, COMMENTS_ROUTE_NAME,
    COMMENT_DATA_CTX, CONTENT_STATUS_CTX, SINGLE_CONTENT_ROUTE_NAMES,
    MODE_QUERY, READ_ONLY_CTX, IS_ASSIGNED_CTX,
    REVIEW_RECORD_CTX, STATUS_BG_CTX, IS_PREVIEW_CTX, IS_REVIEW_CTX,
    OPINION_CONTENT_STATUS_CTX, SUBMIT_URL_CTX, COMMENT_OFFSET_CTX
)
from opinions.enums import ReactionStatus, ViewMode
from opinions.forms import CommentForm, ReportForm
from opinions.models import Comment
from opinions.contexts.comment import (
    get_comment_bundle_context, comments_list_context_for_opinion
)
from opinions.queries import (
    content_status_check, effective_content_status, content_review_records_list
)
from opinions.reactions import COMMENT_REACTIONS, get_reaction_status
from opinions.views.comment_create import get_comment_offset
from opinions.views.opinion_by_id import (
    like_patch, report_post, hide_patch, follow_patch, review_status_patch,
    review_decision_post, TITLE_UPDATE
)
from opinions.views.utils import (
    opinion_permission_check, comment_permission_check, DEFAULT_COMMENT_DEPTH,
    published_check, own_content_check, add_content_no_show_markers,
    get_query_args, QueryOption, STATUS_BADGES, get_comment_context,
    add_review_form_context, timestamp_content, content_save_query_args,
    resolve_ref
)
from soapbox import PATCH, POST, OPINIONS_APP_NAME, HOME_ROUTE_NAME
from utils import (
    Crud, app_template_path, reverse_q, namespaced_url,
    redirect_on_success_or_render
)


class CommentTemplate(Enum):
    """ Enum representing possible response templates for comments """
    BUNDLE_TEMPLATE = \
        app_template_path(
            OPINIONS_APP_NAME, "snippet", "comment_bundle.html"),
    """ Template for individual comments in view opinion, comment list """
    COMMENT_LIST_TEMPLATE = app_template_path(
        OPINIONS_APP_NAME, "snippet", "comment.html")
    """ Template for individual comments in comment list """
    COMMENT_VIEW_TEMPLATE = app_template_path(
        OPINIONS_APP_NAME, "comment_view.html")
    """ Template for comments by id/slug """


CommentTemplate.DEFAULT = CommentTemplate.BUNDLE_TEMPLATE


COMMENT_DETAIL_QUERY_ARGS = [
    QueryOption(MODE_QUERY, ViewMode, ViewMode.DEFAULT),
]


class CommentDetail(LoginRequiredMixin, View):
    """
    Class-based view for individual comment view
    """

    def get(self, request: HttpRequest,
            identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        GET method for Comment
        :param request: http request
        :param identifier: id or slug of opinion to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        comment_permission_check(request, Crud.READ)

        comment_obj = self._get_comment(identifier)
        opinion_obj = comment_obj.opinion

        # get query params
        query_params = get_query_args(request, COMMENT_DETAIL_QUERY_ARGS)
        mode = query_params.get(MODE_QUERY).value

        # perform own comment check
        is_own = own_content_check(
            request, comment_obj,
            raise_ex=mode == ViewMode.EDIT)

        # perform published check, other users don't have access to
        # unpublished comments
        published_check(request, comment_obj)

        # read only if specifically requested, or not current user's comment
        read_only = True if mode.is_non_edit_mode else \
            kwargs.get(READ_ONLY_CTX, not is_own)
        is_preview = comment_obj.status.name == STATUS_PREVIEW or \
            mode == ViewMode.PREVIEW
        is_review = mode == ViewMode.REVIEW

        # ok to view check
        content_status = content_status_check(
            comment_obj, current_user=request.user)
        if content_status.deleted:
            read_only = True
        opinion_content_status = content_status_check(
            opinion_obj, current_user=request.user)
        # users can always view their own comments
        view_ok = is_own \
            if not content_status.view_ok else content_status.view_ok
        effective_status = effective_content_status(comment_obj)
        comment_data = CommentData(comment_obj)
        comments_review_status = get_comments_review_status(
            comment_data, current_user=request.user)

        render_args = {
            READ_ONLY_CTX: read_only,
            VIEW_OK_CTX: view_ok,
            COMMENT_CTX: comment_data,
            OPINION_CTX: opinion_obj,
            STATUS_CTX: effective_status.display,
            IS_PREVIEW_CTX: is_preview,
            IS_REVIEW_CTX: is_review,
            OPINION_CONTENT_STATUS_CTX: opinion_content_status,
            CONTENT_STATUS_CTX: comments_review_status,
        }
        if is_review:
            is_assigned = content_status.assigned_view
            add_review_form_context(
                mode, effective_status, context=render_args)
            render_args.update({
                IS_ASSIGNED_CTX: is_assigned,
                REVIEW_RECORD_CTX: content_review_records_list(comment_obj),
                STATUS_BG_CTX: STATUS_BADGES,
            })

        if comment_permission_check(
                request, Crud.READ, raise_ex=False):
            # get first page comments on comment
            comments_list_context_for_opinion(
                get_comment_query_args(
                    opinion=opinion_obj, parent=comment_obj),
                request.user,
                reaction_ctrls=get_reaction_status(
                    request.user, comment_data
                ),
                context=render_args
            )

        if read_only:
            # viewing comment
            renderer = _render_view
            render_args.update({
                USER_CTX: request.user,
            })
            render_args.update({
                   # visible opinion which may have not visible
                   # under review comments
                   COMMENT_FORM_CTX: CommentForm(),
                   REPORT_FORM_CTX: ReportForm(),
               } if view_ok else
                    # not visible under review opinion
                    add_content_no_show_markers()
            )
        else:
            # updating comment
            renderer = _render_comment_form
            render_args.update({
                SUBMIT_URL_CTX: self.url(comment_obj),
                COMMENT_FORM_CTX: CommentForm(instance=comment_obj),
            })

        template_path, context = renderer(
            f'Comment on {opinion_obj.title}' if read_only else TITLE_UPDATE,
            **render_args
        )
        return render(request, template_path, context=context)

    def post(self, request: HttpRequest,
             identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        POST method to update Comment
        :param request: http request
        :param identifier: id or slug of comment to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        comment_permission_check(request, Crud.UPDATE)

        comment_obj = self._get_comment(identifier)
        success = True                      # default to success
        success_route = HOME_ROUTE_NAME     # on success default route
        success_args = []                   # on success route args

        # perform own comment check
        own_content_check(request, comment_obj)

        form = CommentForm(data=request.POST, files=request.FILES,
                           instance=comment_obj)

        if form.is_valid():
            status, query = content_save_query_args(request)
            comment_obj.status = status

            timestamp_content(comment_obj)

            # save updated object
            comment_obj.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            template_path, context = None, None
        else:
            template_path, context = _render_comment_form(
                TITLE_UPDATE, **{
                    SUBMIT_URL_CTX: self.url(comment_obj),
                    COMMENT_FORM_CTX: form,
                    OPINION_CTX: comment_obj,
                    STATUS_CTX: comment_obj.status
                })
            success = False

        return redirect_on_success_or_render(
            request, success, success_route, *success_args,
            template_path=template_path, context=context)

    def delete(self, request: HttpRequest,
               identifier: [int, str], *args, **kwargs) -> HttpResponse:
        """
        DELETE method to erase Comment content
        Note: just comment contents are erased, as totally removing a comment
              from a comment tree is too problematic
        :param request: http request
        :param identifier: id or slug of comment to erase
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        comment_permission_check(request, Crud.READ)

        comment_obj = self._get_comment(identifier)

        # perform own comment check
        own_content_check(request, comment_obj, raise_ex=True)

        template = CommentTemplate.DEFAULT
        called_by = resolve_ref(request)
        if called_by:
            if called_by.url_name in [
                COMMENTS_ROUTE_NAME
            ]:
                template = CommentTemplate.COMMENT_LIST_TEMPLATE
            elif called_by.url_name in SINGLE_CONTENT_ROUTE_NAMES:
                template = CommentTemplate.BUNDLE_TEMPLATE
            else:
                raise ValueError(
                    f'Unknown {REFERENCE_QUERY} query value: '
                    f'{request.GET[REFERENCE_QUERY]}')

        comment_obj.content = ""
        comment_obj.status = Status.objects.get(**{
            f'{Status.NAME_FIELD}': STATUS_DELETED
        })
        comment_obj.save()

        return get_render_comment_response(
            request, comment_obj.id, template=template)

    @staticmethod
    def _get_comment(identifier: [int, str]) -> Comment:
        """
        Get opinion for specified identifier
        :param identifier: id or slug of opinion to get
        :return: opinion
        """
        query = {
            Comment.id_field() if isinstance(identifier, int)
            else Comment.SLUG_FIELD: identifier
        }
        return get_object_or_404(Comment, **query)

    def url(self, comment_obj: Comment) -> str:
        """
        Get url for comment view/update/delete
        :param comment_obj: opinion
        :return: url
        """
        raise NotImplementedError(
            "'url' method must be overridden by sub classes")


def _render_view(title: str, **kwargs):
    """
    Render the comment view
    :param title: title
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = get_comment_context(title, **kwargs)

    # get reaction controls for opinion & comments
    reaction_ctrls = kwargs.get(TEMPLATE_REACTION_CTRLS, {})

    context.update({
        TEMPLATE_COMMENT_REACTIONS: COMMENT_REACTIONS,
        TEMPLATE_REACTION_CTRLS: reaction_ctrls,
    })

    return app_template_path(
        OPINIONS_APP_NAME, "comment_view.html"), context


def _render_comment_form(title: str, **kwargs) -> tuple[
        str, dict[str, Comment | list[str] | CommentForm | bool]]:
    """
    Render the comment template
    :param title: title
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = get_comment_context(title, **kwargs)

    return app_template_path(OPINIONS_APP_NAME, "comment_form.html"), context


class CommentDetailById(CommentDetail):
    """
    Class-based view for individual comment view/update/delete by id
    """

    def get(self, request: HttpRequest,
            pk: int, *args, **kwargs) -> HttpResponse:
        """
        GET method for Comment
        :param request: http request
        :param pk: id of comment to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().get(request, pk, *args, **kwargs)

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to update Comment
        :param request: http request
        :param pk: id of comment to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().post(request, pk, *args, **kwargs)

    def delete(self, request: HttpRequest, pk: int,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to erase Comment content
        Note: just comment contents are erased, as totally removing a comment
              from a comment tree is too problematic
        :param request: http request
        :param pk: id of comment to erase
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().delete(request, pk, *args, **kwargs)

    def url(self, comment_obj: Comment) -> str:
        """
        Get url for comment view/update/delete
        :param comment_obj: comment
        :return: url
        """
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, COMMENT_ID_ROUTE_NAME),
            args=[comment_obj.id])


class CommentDetailBySlug(CommentDetail):
    """
    Class-based view for individual comment view/update/delete by slug
    """

    def get(self, request: HttpRequest,
            slug: str, *args, **kwargs) -> HttpResponse:
        """
        GET method for Comment
        :param request: http request
        :param slug: slug of comment to get
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().get(request, slug, *args, **kwargs)

    def post(self, request: HttpRequest, slug: str,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to update Comment
        :param request: http request
        :param slug: slug of comment to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().post(request, slug, *args, **kwargs)

    def delete(self, request: HttpRequest, slug: str,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to erase Comment content
        Note: just comment contents are erased, as totally removing a comment
              from a comment tree is too problematic
        :param request: http request
        :param slug: slug of comment to erase
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super().delete(request, slug, *args, **kwargs)

    def url(self, comment_obj: Comment) -> str:
        """
        Get url for comment view/update/delete
        :param comment_obj: comment
        :return: url
        """
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, COMMENT_SLUG_ROUTE_NAME),
            args=[comment_obj.slug])


@login_required
@require_http_methods([PATCH])
def comment_like_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update comment like status.
    :param request: http request
    :param pk:      id of opinion
    :return: http response
    """
    comment_permission_check(request, Crud.READ)

    return like_patch(request, Comment, pk)


@login_required
@require_http_methods([POST])
def comment_report_post(request: HttpRequest, pk: int) -> JsonResponse:
    """
    View function to update opinion report status.
    :param request: http request
    :param pk:      id of opinion
    :return: http response
    """
    comment_permission_check(request, Crud.READ)

    return report_post(request, Comment, pk)


@login_required
@require_http_methods([PATCH])
def comment_review_status_patch(
        request: HttpRequest, pk: int) -> JsonResponse:
    """
    View function to update comment review status.
    :param request: http request
    :param pk:      id of comment
    :return: http response
    """
    comment_permission_check(request, Crud.UPDATE)

    return review_status_patch(request, Comment, pk)


@login_required
@require_http_methods([POST])
def comment_review_decision_post(
        request: HttpRequest, pk: int) -> JsonResponse:
    """
    View function to update comment review decision status.
    :param request: http request
    :param pk:      id of comment
    :return: http response
    """
    comment_permission_check(request, Crud.UPDATE)

    return review_decision_post(request, Comment, pk)


@login_required
@require_http_methods([PATCH])
def comment_hide_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update comment hide status.
    :param request: http request
    :param pk:      id of opinion
    :return:
    """
    opinion_permission_check(request, Crud.READ)

    response = hide_patch(request, Comment, pk)
    if response.status_code == HTTPStatus.OK:
        # change response to updated html rather than default redirect
        status = ReactionStatus.from_arg(
            json.loads(response.content)[STATUS_CTX]
        )

        _ = get_object_or_404(Comment, pk=pk)

        response = get_render_comment_response(
            request, pk,
            depth=DEFAULT_COMMENT_DEPTH if status == ReactionStatus.SHOW
            else 0
        )

    return response


def get_render_comment_response(
    request: HttpRequest, pk: int, depth: int = DEFAULT_COMMENT_DEPTH,
    template: CommentTemplate = CommentTemplate.DEFAULT
) -> JsonResponse:
    """
    Get a render response for the comment with the specified id
    :param request: http request
    :param pk: id of comment
    :param depth: comment depth; default DEFAULT_COMMENT_DEPTH
    :param template: template to use for comment html in response;
            default CommentTemplate.DEFAULT
    :return: response
    """
    comment = Comment.objects.get(**{
        f'{Comment.id_field()}': pk
    })
    if template == CommentTemplate.BUNDLE_TEMPLATE:
        element_id = f'id--comment-section-{pk}'
        context = get_comment_bundle_context(pk, request.user, depth=depth)
    else:
        element_id = f'id--comment-card-{pk}'
        comment = Comment.objects.get(**{
            f'{Comment.id_field()}': pk
        })
        comment_data = CommentData(comment)
        # get review status of comments
        comments_review_status = get_comments_review_status(
            comment_data, current_user=request.user)

        context = {
            COMMENT_DATA_CTX: comment_data,
            CONTENT_STATUS_CTX: comments_review_status,
        }
        add_content_no_show_markers(context=context)

    comment_offset, top_level = get_comment_offset(request, comment)
    context[COMMENT_OFFSET_CTX] = comment_offset

    return JsonResponse({
        ELEMENT_ID_CTX: element_id,
        HTML_CTX: render_to_string(
            template.value, context=context, request=request)
    }, status=HTTPStatus.OK)


@login_required
@require_http_methods([PATCH])
def comment_follow_patch(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update follow comment author status.
    :param request: http request
    :param pk:      id of author
    :return: http response
    """
    comment_permission_check(request, Crud.READ)

    return follow_patch(request, Comment, pk)
