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

from opinions.comment_data import (
    get_comment_tree, get_comments_review_status, get_comment_query_args
)
from opinions.constants import (
    IS_PREVIEW_CTX, ALL_FIELDS, UNDER_REVIEW_CONTENT_CTX,
    UNDER_REVIEW_COMMENT_CONTENT, HIDDEN_CONTENT_CTX, HIDDEN_COMMENT_CONTENT,
    COMMENTS_CTX, CONTENT_STATUS_CTX, TEMPLATE_COMMENT_REACTIONS,
    TEMPLATE_REACTION_CTRLS, TEMPLATE_COMMENT_BUNDLE
)
from opinions.enums import QueryArg
from opinions.reactions import get_reaction_status, COMMENT_REACTIONS
from opinions.views.utils import DEFAULT_COMMENT_DEPTH
from user.models import User


def comments_list_context_for_opinion(
    query_params: dict[str, QueryArg], user: User,
    context: Optional[dict] = None, reaction_ctrls: Optional[dict] = None
) -> dict:
    """
    Get the context and comment list for an opinion display
    :param query_params: query parameters
    :param user: current user
    :param context: context object to update; default None
    :param reaction_ctrls: reaction controls object to update; default None
    :return: context object
    """
    if context is None:
        context = {}
    if reaction_ctrls is None:
        reaction_ctrls = {}

    # get first page comments for opinion
    comment_bundles = get_comment_tree(query_params, user)
    # get review status of comments
    comments_review_status = get_comments_review_status(comment_bundles)

    # reaction controls for comments
    is_preview = context.get(IS_PREVIEW_CTX, False)
    reaction_ctrls.update(
        get_reaction_status(
            user, comment_bundles,
            # no reactions for opinion preview
            enablers={ALL_FIELDS: False} if is_preview else None)
    )

    # visible opinion which may have not visible under review comments
    context.update({
        UNDER_REVIEW_CONTENT_CTX: UNDER_REVIEW_COMMENT_CONTENT,
        HIDDEN_CONTENT_CTX: HIDDEN_COMMENT_CONTENT,
        COMMENTS_CTX: comment_bundles,
        CONTENT_STATUS_CTX: comments_review_status,
        TEMPLATE_COMMENT_REACTIONS: COMMENT_REACTIONS,
        TEMPLATE_REACTION_CTRLS: reaction_ctrls,
    })
    return context


def get_comment_bundle_context(
    pk: int, user: User, depth: int = DEFAULT_COMMENT_DEPTH,
    context: Optional[dict] = None, reaction_ctrls: Optional[dict] = None,
    is_dynamic_insert: bool = False
) -> dict:
    """
    Get the context for use with 'comment_bundle.html'
    :param pk: id of comment
    :param user: current user
    :param depth: comment depth: default DEFAULT_COMMENT_DEPTH
    :param context: context object to update; default None
    :param reaction_ctrls: reaction controls object to update; default None
    :param is_dynamic_insert: is a dynamic insert flag; default False
    :return: context dict
    """
    query_params = get_comment_query_args(comment=pk, depth=depth)
    context = comments_list_context_for_opinion(
        query_params, user, context=context, reaction_ctrls=reaction_ctrls)
    # comment template expects: 'bundle' as CommentBundle, so transform
    # CommentBundle list
    assert len(context[COMMENTS_CTX]) == 1
    context[TEMPLATE_COMMENT_BUNDLE] = context[COMMENTS_CTX][0]
    del context[COMMENTS_CTX]
    context[TEMPLATE_COMMENT_BUNDLE].dynamic_insert = is_dynamic_insert

    return context
