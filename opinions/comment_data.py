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
from datetime import datetime
from typing import Union, List, Optional, Type
from itertools import chain

from categories import REACTION_AGREE, REACTION_DISAGREE
from categories.models import Status
from soapbox import AVATAR_BLANK_URL, OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url, ModelFacadeMixin, ensure_list
from .constants import (
    PAGE_QUERY, PER_PAGE_QUERY, PARENT_ID_QUERY, COMMENT_DEPTH_QUERY,
    COMMENT_MORE_ROUTE_NAME, OPINION_ID_QUERY, ID_QUERY, OPINION_CTX
)
from .models import Comment, Opinion, AgreementStatus, HideStatus, PinStatus
from .comment_utils import get_comment_queryset
from .views.utils import (
    DEFAULT_COMMENT_DEPTH, query_search_term
)
from .enums import QueryArg, PerPage
from .queries import content_status_check

REPLY_CONTAINER_ID = 'id--comment-collapse'
REPLY_MORE_CONTAINER_ID = f'{REPLY_CONTAINER_ID}-more'


class CommentData(ModelFacadeMixin):
    """ Data class represent a comment """
    comment: Comment
    """ Comment """

    def __init__(self, comment: Comment):
        self.comment = comment

    def lookup_clazz(self):
        """ Get the Model class """
        return Comment

    @property
    def avatar_url(self):
        """ Get avatar url of comment author """
        return AVATAR_BLANK_URL \
            if User.AVATAR_BLANK in self.comment.user.avatar.url \
            else self.comment.user.avatar.url

    # Properties allowing CommentData to appear like Comment
    # TODO revisit CommentData there must be a better approach?

    @property
    def id(self) -> int:
        """ Get comment id """
        return self.comment.id

    @property
    def content(self) -> str:
        """ Get comment content """
        return self.comment.content

    @property
    def opinion(self) -> Opinion:
        """ Get comment opinion """
        return self.comment.opinion

    @property
    def parent(self) -> int:
        """ Get comment parent """
        return self.comment.parent

    @property
    def level(self) -> int:
        """ Get comment level """
        return self.comment.level

    @property
    def user(self) -> int:
        """ Get comment author """
        return self.comment.user

    @property
    def status(self) -> Status:
        """ Get comment author """
        return self.comment.status

    @property
    def slug(self) -> str:
        """ Get comment slug """
        return self.comment.slug

    @property
    def created(self) -> datetime:
        """ Get comment created """
        return self.comment.created

    @property
    def updated(self) -> datetime:
        """ Get comment updated """
        return self.comment.updated

    @property
    def published(self) -> datetime:
        """ Get comment published """
        return self.comment.published

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
    comment_query: [str, None]
    """ Query to get sub-level comments """
    dynamic_insert: bool
    """ Object was dynamically inserted, so is not in correct location """
    collapse_id: str
    """ Id for comment collapse """
    next_page: [str, None]
    """ Url to request next page of a CommentBundle list """

    def __init__(self, comment: Comment, comments: list[CommentData] = None):
        super().__init__(comment)
        self.comments = [] if comments is None else comments
        self.collapse_id = CommentBundle.generate_collapse_id(comment.id)
        self.next_page = None
        self.comment_query = None
        self.dynamic_insert = False

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


def get_comment_query_args(
        opinion: Union[int, Opinion] = None,
        comment: Union[int, Comment] = None,
        parent: Union[int, Comment] = None,
        depth: int = DEFAULT_COMMENT_DEPTH,
        page: int = 1, per_page: PerPage = PerPage.DEFAULT
) -> dict[str, QueryArg]:
    """
    Get comment query args
    :param opinion: opinion (id or object) to get comments for; default None
    :param comment: comment (id or object) to get comments for; default None
    :param parent: parent (id or object) to get comments for; default None
    :param depth: comment depth; default DEFAULT_COMMENT_DEPTH
    :param page: 1-based page number to get; default 1
    :param per_page: options per page; default PerPage.DEFAULT
    :return: query args for list of comments
    """
    arg_list = [
        (PAGE_QUERY, page),
        (PER_PAGE_QUERY, per_page),
        (COMMENT_DEPTH_QUERY, depth)
    ]
    if opinion:
        if isinstance(opinion, Opinion):
            opinion = opinion.id
        else:
            assert isinstance(opinion, int), \
                f"Expected [Opinion, int] got {type(opinion)} {opinion}"
        arg_list.append(
            (OPINION_ID_QUERY, opinion)
        )

    if comment:
        if isinstance(comment, Comment):
            comment = comment.id
        else:
            assert isinstance(comment, int),\
                f"Expected [Comment, int] got {type(comment)} {comment}"
        arg_list.append(
            (ID_QUERY, comment)
        )

    parent_query = None
    if parent:
        if isinstance(parent, Comment):
            parent = parent.id
        else:
            assert isinstance(parent, int),\
                f"Expected [Comment, int] got {type(parent)} {parent}"
        parent_query = (PARENT_ID_QUERY, parent)
    elif comment is None:
        parent_query = (PARENT_ID_QUERY, Comment.NO_PARENT)

    if parent_query:
        arg_list.append(parent_query)

    return {
        q: QueryArg(v, True) for q, v in arg_list
    }


def get_comment_tree(
    query_params: dict[str, QueryArg], user: User
) -> list[CommentBundle]:
    """
    Get comment tree, i.e. comments and comments on those comments etc.
    :param query_params: query parameters
    :param user: current user
    :return: list of comments (including a 'more' element if necessary)
    """
    # get first level comments
    comment_bundles = get_comments_page(query_params, user)

    depth = query_params.get(COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH)
    if isinstance(depth, QueryArg):
        depth = depth.value_arg_or_value

    sub_query_params = query_params.copy()
    if depth > 1:
        if Comment.id_field() in sub_query_params:
            # remove comment id if present
            del sub_query_params[Comment.id_field()]

        # get first page of comments on comments
        sub_query_params[PAGE_QUERY] = 1
        sub_query_params[COMMENT_DEPTH_QUERY] = depth - 1

        def next_level_comments(
                bundle: CommentBundle, sq_params: dict[str, QueryArg]):
            # recursive call to get next level comments
            bundle.comments = get_comment_tree(sq_params, user)

        next_level_func = next_level_comments
    else:
        # check if there are sub-level comments for another request
        page = QueryArg.value_arg_or_object(
            sub_query_params[PAGE_QUERY]) \
            if PAGE_QUERY in sub_query_params else 1
        sub_query_params[PAGE_QUERY] = page
        sub_query_params[COMMENT_DEPTH_QUERY] = DEFAULT_COMMENT_DEPTH

        # convert opinion query to opinion id query
        if OPINION_CTX in sub_query_params:
            opinion = sub_query_params[OPINION_CTX]
            sub_query_params[OPINION_ID_QUERY] = \
                QueryArg.value_arg_or_value(opinion).id
            del sub_query_params[OPINION_CTX]

        def next_level_query(
                bundle: CommentBundle, sq_params: dict[str, QueryArg]):
            # query to retrieve next level comments
            query_set = get_comment_queryset(sq_params, user)
            if query_set.exists():
                bundle.comment_query = query_search_term(sq_params)

        next_level_func = next_level_query

    for comment_bundle in comment_bundles:
        if comment_bundle.is_more_placeholder:
            continue
        sub_query_params[PARENT_ID_QUERY] = comment_bundle.comment.id
        next_level_func(comment_bundle, sub_query_params)

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
        PER_PAGE_QUERY, PerPage.DEFAULT).value_arg_or_value
    page = query_params.get(PAGE_QUERY, 1)
    if isinstance(page, QueryArg):
        page = page.value_arg_or_value
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
        next_query_params = {}
        for qry, val in query_params.items():
            if not isinstance(val, QueryArg):
                next_query_params[qry] = val
            elif isinstance(val, QueryArg) and val.was_set:
                # filter out unset query params
                next_query_params[qry] = val.value_arg_or_value

        next_query_params[PAGE_QUERY] = page + 1
        next_query_params[PER_PAGE_QUERY] = per_page

        comments[-1].set_placeholder(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, COMMENT_MORE_ROUTE_NAME),
                query_kwargs=next_query_params
            ))

    return comments


def get_comments_review_status(
    comment_bundles: [Type[CommentData], List[Type[CommentData]]],
    comments_review_status: Optional[dict] = None,
    current_user: User = None
):
    """
    Get the review status of content
    :param comment_bundles: CommentBundle(s) to get review statuses of
    :param comments_review_status: dict to add to; default None
    :param current_user: user making request; default None
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
            cmt.id: content_status_check(cmt, current_user=current_user)
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
