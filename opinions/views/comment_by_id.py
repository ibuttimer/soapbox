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
from django.http import (
    HttpRequest, HttpResponse, JsonResponse
)
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from opinions.constants import STATUS_CTX
from opinions.enums import ReactionStatus
from opinions.models import (
    Comment
)
from opinions.contexts.comment import get_comment_bundle_context
from opinions.views.opinion_by_id import like_patch, report_post, hide_patch
from opinions.views.utils import (
    opinion_permission_check, comment_permission_check, DEFAULT_COMMENT_DEPTH
)
from soapbox import (
    PATCH, POST, OPINIONS_APP_NAME
)
from utils import (
    Crud, app_template_path
)


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
            depth=DEFAULT_COMMENT_DEPTH
            if status == ReactionStatus.SHOW else 0
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
