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
from collections import namedtuple
from typing import Union, List, Optional, Type
from itertools import chain

from categories import REACTION_AGREE, REACTION_DISAGREE
from categories.models import Status
from soapbox import AVATAR_BLANK_URL, OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .constants import (
    PAGE_QUERY, PER_PAGE_QUERY, PARENT_ID_QUERY, COMMENT_DEPTH_QUERY,
    COMMENT_MORE_ROUTE_NAME, OPINION_ID_QUERY
)
from .models import Comment, Opinion, AgreementStatus, HideStatus, PinStatus
from .comment_utils import get_comment_queryset
from opinions.views.utils import DEFAULT_COMMENT_DEPTH, ensure_list
from .enums import QueryArg, PerPage
from .queries import content_status_check

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
            else self.comment.user.avatar.url

    @property
    def id(self):
        """ Get comment """
        return self.comment.id

    def comment_iterable(self) -> chain[Comment]:
        """
        Generate an iterator that cycles through all the comments in this
        object, i.e. the comment
        :return: iterator
        """
        return chain([self.comment])

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

    def comment_iterable(self) -> chain[Comment]:
        """
        Generate an iterator that cycles through all the comments in this
        object, i.e. the comment, any replies to the comment,
        any replies to the replies etc.
        :return: iterator
        """
        return chain([self.comment], chain.from_iterable(list(
            map(lambda cmt: list(cmt.comment_iterable()), self.comments)
        )))


def get_comment_tree(
        query_params: Union[int, dict[str, QueryArg]], user: User
) -> list[CommentBundle]:
    """
    Get comment tree, i.e. comments and comments on those comments etc.
    :param query_params: query parameters or opinion id; default
                page 1, PerPage.DEFAULT, DEFAULT_COMMENT_DEPTH
    :param user: current user
    :return: list of comments (including a 'more' element if necessary)
    """
    if isinstance(query_params, int):
        query_params = {
            q: QueryArg(v, True) for q, v in [
                (OPINION_ID_QUERY, query_params),
                (PARENT_ID_QUERY, Comment.NO_PARENT),
                (PAGE_QUERY, 1),
                (PER_PAGE_QUERY, PerPage.DEFAULT),
                (COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH)
            ]
        }

    # get first level comments
    comment_bundles = get_comments_page(query_params, user)

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
                get_comment_tree(sub_query_params, user)

    return comment_bundles


def get_comments_page(
        query_params: dict[str, QueryArg], user: User) -> list[CommentBundle]:
    """
    Get a page of comments, i.e. comments on opinion/comment
    :param query_params: query parameters; default page 1, PerPage.DEFAULT
    :param user: current user
    :return: list of comments (including a 'more' element if necessary)
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
    add_more_placeholder = end < count
    if add_more_placeholder:
        end += 1    # add extra for more placeholder

    comments = [
        CommentBundle(comment) for comment in list(query_set[start:end])
    ]

    if add_more_placeholder:
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


def get_comments_review_status(
    comment_bundles: [Type[CommentData], List[Type[CommentData]]],
    comments_review_status: Optional[dict] = None
):
    """
    Get the review status of content
    :param comment_bundles: CommentBundle(s) to get review statuses of
    :param comments_review_status: dict to add to; default None
    :return: dict of the form {
                   key: comment id
                   value: ContentStatus
               }
    """
    if comments_review_status is None:
        comments_review_status = {}

    # get review status of comments
    for comment in ensure_list(comment_bundles):
        comments_review_status.update({
            # key: comment id, value: ContentStatus
            cmt.id: content_status_check(cmt)
            for cmt in comment.comment_iterable()
        })

    return comments_review_status


PopularityLevel = namedtuple("PopularityLevel", [
    "comments",     # comments count
    "agree",        # agrees count
    "disagree",     # disagrees count
    "hide",         # hide count
    "pin",          # pin count
], defaults=[0, 0, 0, 0, 0])


def get_popularity_levels(opinions: Union[Opinion, list[Opinion]]) -> dict:
    """
    Get popularity levels for specified opinion(s)
    :param opinions: opinion ot list of opinions
    :return: dict with 'opinion_<id>' as the key and PopularityLevel value
    """
    if isinstance(opinions, Opinion):
        opinions = [opinions]
    levels = {}

    for opinion in opinions:
        levels[f'opinion_{opinion.id}'] = PopularityLevel(
            comments=Comment.objects.filter(**{
                f'{Comment.OPINION_FIELD}': opinion
            }).count(),
            agree=AgreementStatus.objects.filter(**{
                f'{AgreementStatus.OPINION_FIELD}': opinion,
                f'{AgreementStatus.STATUS_FIELD}__{Status.NAME_FIELD}':
                    REACTION_AGREE
            }).count(),
            disagree=AgreementStatus.objects.filter(**{
                f'{AgreementStatus.OPINION_FIELD}': opinion,
                f'{AgreementStatus.STATUS_FIELD}__{Status.NAME_FIELD}':
                    REACTION_DISAGREE
            }).count(),
            hide=HideStatus.objects.filter(**{
                f'{HideStatus.OPINION_FIELD}': opinion
            }).count(),
            pin=PinStatus.objects.filter(**{
                f'{PinStatus.OPINION_FIELD}': opinion
            }).count(),
        )

    return levels
