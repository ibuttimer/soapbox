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
from soapbox import AVATAR_BLANK_URL, OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .constants import (
    PAGE_QUERY, PER_PAGE_QUERY, PARENT_ID_QUERY, COMMENT_DEPTH_QUERY,
    COMMENT_MORE_ROUTE_NAME
)
from .models import Comment
from .comment_utils import get_comment_queryset
from .views_utils import DEFAULT_COMMENT_DEPTH
from .enums import QueryArg, PerPage

REPLY_CONTAINER_ID = 'id--comment-collapse'
REPLY_MORE_CONTAINER_ID = f'{REPLY_CONTAINER_ID}-more'


class CommentData:
    """ Data class represent a comment """
    comment: Comment
    """ Comment """

    def __init__(self, comment: Comment):
        self.comment = comment

    @property
    def avatar_url(self):
        """ Get avatar url of comment author """
        return AVATAR_BLANK_URL \
            if User.AVATAR_BLANK in self.comment.user.avatar.url \
            else self.comment.user.avatar

    def __str__(self):
        return f'{self.comment.level}: {self.comment}'


class CommentBundle(CommentData):
    """
    Data class represent a comment bundle or a placeholder for more in a list
    """
    comments: list[CommentData]
    """ Replies to comment """
    collapse_id: str
    """ Id for comment collapse """
    next_page: [str, None]
    """ Url to request next page of a CommentBundle list """

    def __init__(self, comment: Comment, comments: list[CommentData] = None):
        super().__init__(comment)
        self.comments = [] if comments is None else comments
        self.collapse_id = CommentBundle.generate_collapse_id(comment.id)
        self.next_page = None

    def __str__(self):
        text = f'{self.comment} {len(self.comments)} replies' \
            if not self.is_more_placeholder else \
            f'{self.next_page}'
        return f'{self.comment.level}: {text}'

    def set_placeholder(self, next_page: str):
        """
        Update object to be a placeholder
        :param next_page: next page url
        """
        self.next_page = next_page
        self.collapse_id = CommentBundle.generate_collapse_id(
            self.comment.id, is_placeholder=True)

    @property
    def is_more_placeholder(self):
        """ Check if object is a more entries placeholder """
        return self.next_page is not None

    @staticmethod
    def generate_collapse_id(
            comment_id: int, is_placeholder: bool = False) -> str:
        """
        Generate a html element id for the collapsable container for replies
        to a comment
        :param comment_id: database id of comment
        :param is_placeholder: generate placeholder id flag
        :return: html element id
        """
        name = REPLY_MORE_CONTAINER_ID if is_placeholder \
            else REPLY_CONTAINER_ID
        return f'{name}-{comment_id}'


def get_comment_bundle(
        query_params: dict[str, QueryArg], user: User) -> list[CommentBundle]:
    """
    Get comment bundle, i.e. comments on opinion and comments on those
    comments
    :param query_params: query parameters
    :param user: current user
    :return: list of comments
    """
    # get first level comments
    comment_bundles = get_comments(query_params, user)

    depth = query_params.get(COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH)
    if isinstance(depth, QueryArg):
        depth = depth.query_arg_value

    if depth > 1:
        sub_query_params = query_params.copy()

        # get first page of comments on comments
        sub_query_params[PAGE_QUERY] = 1
        sub_query_params[COMMENT_DEPTH_QUERY] = depth - 1

        for comment_bundle in comment_bundles:
            sub_query_params[PARENT_ID_QUERY] = comment_bundle.comment.id
            # recursive call to get next level comments
            comment_bundle.comments = \
                get_comment_bundle(sub_query_params, user)

    return comment_bundles


def get_comments(
        query_params: dict[str, QueryArg], user: User) -> list[CommentBundle]:
    """
    Get comment bundle, i.e. comments on opinion/comment
    :param query_params: query parameters
    :param user: current user
    :return: list of comments
    """
    query_set = get_comment_queryset(query_params, user)

    per_page = query_params.get(
        PER_PAGE_QUERY, PerPage.DEFAULT).query_arg_value
    page = query_params.get(PAGE_QUERY, 1)
    if isinstance(page, QueryArg):
        page = page.query_arg_value
    start = per_page * (page - 1)
    end = start + per_page

    count = query_set.count()
    add_placeholder = end < count
    if add_placeholder:
        end += 1    # add extra for more placeholder

    comments = [
        CommentBundle(comment) for comment in list(query_set[start:end])
    ]

    if add_placeholder:
        # set placeholder for more
        next_query_params = query_params.copy()
        next_query_params[PAGE_QUERY] = page + 1
        next_query_params[PER_PAGE_QUERY] = per_page
        for q, v in next_query_params.items():
            if isinstance(v, QueryArg):
                next_query_params[q] = v.query_arg_value

        comments[-1].set_placeholder(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, COMMENT_MORE_ROUTE_NAME),
                query_kwargs=next_query_params
            ))

    return comments
