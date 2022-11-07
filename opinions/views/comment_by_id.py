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

from opinions.comment_data import get_comment_query_args
from opinions.constants import (
    STATUS_CTX, VIEW_OK_CTX, COMMENT_CTX, TEMPLATE_REACTION_CTRLS, USER_CTX,
    TEMPLATE_COMMENT_REACTIONS, COMMENT_ID_ROUTE_NAME,
    COMMENT_SLUG_ROUTE_NAME, OPINION_CTX, COMMENT_FORM_CTX, REPORT_FORM_CTX,
    UNDER_REVIEW_TITLE_CTX, UNDER_REVIEW_EXCERPT_CTX,
    UNDER_REVIEW_CONTENT_CTX, UNDER_REVIEW_TITLE, UNDER_REVIEW_EXCERPT,
    UNDER_REVIEW_OPINION_CONTENT
)
from opinions.enums import ReactionStatus
from opinions.forms import CommentForm, ReviewForm
from opinions.models import Comment
from opinions.contexts.comment import (
    get_comment_bundle_context, comments_list_context_for_opinion
)
from opinions.queries import content_status_check
from opinions.reactions import COMMENT_REACTIONS
from opinions.views.opinion_by_id import (
    like_patch, report_post, hide_patch, follow_patch
)
from opinions.views.utils import (
    opinion_permission_check, comment_permission_check, DEFAULT_COMMENT_DEPTH,
    published_check, own_content_check
)
from soapbox import PATCH, POST, OPINIONS_APP_NAME
from utils import (
    Crud, app_template_path, reverse_q, namespaced_url
)


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

        # perform own comment check
        is_own = own_content_check(request, comment_obj, raise_ex=False)

        # perform published check, other users don't have access to
        # unpublished opinions
        published_check(request, comment_obj)

        # ok to view check
        content_status = content_status_check(comment_obj)
        # users can always view their own comments
        view_ok = is_own \
            if not content_status.view_ok else content_status.view_ok

        render_args = {
            VIEW_OK_CTX: view_ok,
            COMMENT_CTX: comment_obj,
            OPINION_CTX: comment_obj.opinion,
            STATUS_CTX: comment_obj.status,
            COMMENT_FORM_CTX: CommentForm(),
            REPORT_FORM_CTX: ReviewForm(),
        }

        # get first page comments
        query_params = get_comment_query_args(
            opinion=comment_obj.opinion, comment=comment_obj)
        render_args = comments_list_context_for_opinion(
            query_params, request.user, context=render_args)

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

        template_path, context = _render_view(**render_args)
        return render(request, template_path, context=context)

    def _get_comment(self, identifier: [int, str]) -> Comment:
        """
        Get opinion for specified identifier
        :param identifier: id or slug of opinion to get
        :return: opinion
        """
        query = {
            Comment.ID_FIELD if isinstance(identifier, int)
            else Comment.SLUG_FIELD: identifier
        }
        return get_object_or_404(Comment, **query)

    def url(self, comment_obj: Comment) -> str:
        """
        Get url for comment view/update
        :param comment_obj: opinion
        :return: url
        """
        raise NotImplementedError(
            "'url' method must be overridden by sub classes")


def _render_view(**kwargs):
    """
    Render the opinion view
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = kwargs.copy()

    # get reaction controls for opinion & comments
    reaction_ctrls = kwargs.get(TEMPLATE_REACTION_CTRLS, {})

    context.update({
        TEMPLATE_COMMENT_REACTIONS: COMMENT_REACTIONS,
        TEMPLATE_REACTION_CTRLS: reaction_ctrls,
    })

    return app_template_path(
        OPINIONS_APP_NAME, "comment_view.html"), context


class CommentDetailById(CommentDetail):
    """
    Class-based view for individual comment view/update by id
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
        return CommentDetail.get(self, request, pk, *args, **kwargs)

    def post(self, request: HttpRequest,
             pk: int, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Comment
        :param request: http request
        :param pk: id of Comment to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return CommentDetail.post(self, request, pk, *args, **kwargs)

    def url(self, opinion_obj: Comment) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, COMMENT_ID_ROUTE_NAME),
            args=[opinion_obj.id])


class CommentDetailBySlug(CommentDetail):
    """
    Class-based view for individual comment view/update by slug
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
        return CommentDetail.get(self, request, slug, *args, **kwargs)

    def post(self, request: HttpRequest,
             slug: str, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Comment
        :param request: http request
        :param slug: slug of comment to update
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return CommentDetail.post(self, request, slug, *args, **kwargs)

    def url(self, opinion_obj: Comment) -> str:
        """
        Get url for opinion view/update
        :param opinion_obj: opinion
        :return: url
        """
        return reverse_q(
            namespaced_url(OPINIONS_APP_NAME, COMMENT_SLUG_ROUTE_NAME),
            args=[opinion_obj.slug])


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

        comment = get_object_or_404(Comment, pk=pk)

        context = get_comment_bundle_context(
            comment.id, request.user,
            depth=DEFAULT_COMMENT_DEPTH if status == ReactionStatus.SHOW
            else 0
        )
        response = JsonResponse({
            'element_id': f'id--comment-section-{pk}',
            'html': render_to_string(
                app_template_path(
                    OPINIONS_APP_NAME, "snippet", "comment_bundle.html"),
                context=context,
                request=request)
        }, status=HTTPStatus.OK)

    return response


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
