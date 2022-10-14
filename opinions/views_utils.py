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
from datetime import datetime
from enum import Enum
from typing import Any, Type

from zoneinfo import ZoneInfo

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.template.defaultfilters import truncatechars
from bs4 import BeautifulSoup

from categories.constants import STATUS_ALL
from soapbox import OPINIONS_APP_NAME
from utils import Crud, app_template_path, permission_check
from categories import (
    STATUS_DRAFT, STATUS_PUBLISHED, STATUS_PREVIEW, STATUS_WITHDRAWN,
    STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW, STATUS_APPROVED,
    STATUS_REJECTED,
    CATEGORY_UNASSIGNED,
    REACTION_AGREE, REACTION_DISAGREE, REACTION_HIDE, REACTION_SHOW,
    REACTION_FOLLOW, REACTION_UNFOLLOW
)
from categories.models import Status, Category
from user.models import User
from .constants import (
    ORDER_QUERY, SEARCH_QUERY, STATUS_QUERY, PER_PAGE_QUERY,
    PAGE_QUERY, TITLE_QUERY, CONTENT_QUERY, CATEGORY_QUERY, AUTHOR_QUERY,
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY, REORDER_QUERY, OPINION_ID_QUERY, PARENT_ID_QUERY,
    COMMENT_DEPTH_QUERY
)
from .models import Opinion, Comment
from .forms import OpinionForm

READ_ONLY = 'read_only'     # read-only mode
DEFAULT_COMMENT_DEPTH = 2


class ChoiceArg(Enum):
    """ Enum representing options with limited choices """
    display: str
    """ Display string """
    arg: Any
    """ Argument value """

    def __init__(self, display: str, arg: Any):
        self.display = display
        self.arg = arg


class QueryArg:
    """ Class representing query args """
    value: Any
    """ Value """
    was_set: bool
    """ Argument was set in request flag """

    def __init__(self, value: Any, was_set: bool):
        self.set(value, was_set)

    def set(self, value: Any, was_set: bool):
        """
        Set the value and was set flag
        :param value:
        :param was_set:
        :return:
        """
        self.value = value
        self.was_set = was_set

    def was_set_to(self, value: Any, attrib: str = None):
        """
        Check if value was to set the specified `value`
        :param value: value to check
        :param attrib: attribute of set value to check; default None
        :return: True if value was to set the specified `value`
        """
        chk_value = self.value if not attrib else getattr(self.value, attrib)
        return self.was_set and chk_value == value

    @property
    def query_arg_value(self):
        """
        Get the arg value of a query argument
        :return: value
        """
        return self.value.arg \
            if isinstance(self.value, ChoiceArg) else self.value

    def __str__(self):
        return f'{self.value}, was_set {self.was_set}'


class QueryStatus(ChoiceArg):
    """ Enum representing status query params """
    ALL = (STATUS_ALL, 'all')
    DRAFT = (STATUS_DRAFT, 'draft')
    PUBLISH = (STATUS_PUBLISHED, 'publish')
    PREVIEW = (STATUS_PREVIEW, 'preview')
    WITHDRAWN = (STATUS_WITHDRAWN, 'withdrawn')
    PENDING_REVIEW = (STATUS_PENDING_REVIEW, 'pending-review')
    UNDER_REVIEW = (STATUS_UNDER_REVIEW, 'under-review')
    APPROVED = (STATUS_APPROVED, 'approved')
    REJECTED = (STATUS_REJECTED, 'rejected')

    def __init__(self, display: str, arg: str):
        super().__init__(display, arg)


class ReactionStatus(ChoiceArg):
    """ Enum representing reactions query params """
    AGREE = (REACTION_AGREE, 'agree')
    DISAGREE = (REACTION_DISAGREE, 'disagree')
    HIDE = (REACTION_HIDE, 'hide')
    SHOW = (REACTION_SHOW, 'show')
    FOLLOW = (REACTION_FOLLOW, 'follow')
    UNFOLLOW = (REACTION_UNFOLLOW, 'unfollow')

    def __init__(self, display: str, arg: str):
        super().__init__(display, arg)


def get_opinion_context(
        title: str, submit_url: str = None, form: OpinionForm = None,
        opinion_obj: Opinion = None, comments: dict = None,
        read_only: bool = False, status: Status = None) -> dict:
    """
    Generate the context for the opinion template
    :param title: title
    :param submit_url: form commit url, default None
    :param form: form to display, default None
    :param opinion_obj: opinion object, default None
    :param comments: details of comments
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

    if comments is not None:
        context['comments'] = comments

    return context


def timestamp_content(content: [Opinion, Comment]):
    """
    Update opinion/comment timestamps
    :param content: opinion/comment to update
    """
    timestamp = datetime.now(tz=ZoneInfo("UTC"))
    content.updated = timestamp
    if content.status.name == STATUS_PUBLISHED:
        if content.published.year == 1:
            # first time published
            content.published = timestamp


def opinion_query_args(
        request: HttpRequest, query: str, clazz: Type[ChoiceArg],
        default: ChoiceArg) -> tuple[Status, Type[ChoiceArg]]:
    """
    Get opinion save query arguments from request query
    :param request: http request
    :param query: query parameter in request
    :param clazz: class of argument
    :param default: default value
    :return: tuple of Status and argument class instance
    """
    # query params are in request.GET
    # maybe slightly unorthodox, but saves defining 3 routes
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = get_query_args(request, [
        (query, clazz, default),
    ])
    status_query = params[query].value
    status = Status.objects.get(name=status_query.display)

    return status, status_query


def opinion_save_query_args(
        request: HttpRequest) -> tuple[Status, QueryStatus]:
    """
    Get opinion save query arguments from request query
    :param request: http request
    :return: tuple of Status and QueryStatus
    """
    return opinion_query_args(
        request, STATUS_QUERY, QueryStatus, QueryStatus.DRAFT)


def opinion_like_query_args(
        request: HttpRequest) -> tuple[Status, ReactionStatus]:
    """
    Get opinion react query arguments from request query
    :param request: http request
    :return: tuple of Status and ReactionStatus
    """
    return opinion_query_args(
        request, STATUS_QUERY, ReactionStatus, ReactionStatus.AGREE)


class SortOrder(ChoiceArg):
    """ Base enum representing sort orders """

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg)
        self.order = order


class OpinionSortOrder(SortOrder):
    """ Enum representing opinion sort orders """
    NEWEST = ('Newest first', 'new', f'-{Opinion.PUBLISHED_FIELD}')
    OLDEST = ('Oldest first', 'old', f'{Opinion.PUBLISHED_FIELD}')
    AUTHOR_AZ = ('Author A-Z', 'aaz',
                 f'{Opinion.USER_FIELD}__{User.USERNAME_FIELD}')
    AUTHOR_ZA = ('Author Z-A', 'aza',
                 f'-{Opinion.USER_FIELD}__{User.USERNAME_FIELD}')
    TITLE_AZ = ('Title A-Z', 'taz', f'{Opinion.TITLE_FIELD}')
    TITLE_ZA = ('Title Z-A', 'tza', f'-{Opinion.TITLE_FIELD}')
    STATUS_AZ = ('Status A-Z', 'saz',
                 f'{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}')
    STATUS_ZA = ('Status Z-A', 'sza',
                 f'-{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}')

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg, order)


OpinionSortOrder.DEFAULT = OpinionSortOrder.NEWEST


class CommentSortOrder(SortOrder):
    """ Enum representing opinion sort orders """
    NEWEST = ('Newest first', 'new', f'-{Comment.PUBLISHED_FIELD}')
    OLDEST = ('Oldest first', 'old', f'{Comment.PUBLISHED_FIELD}')
    AUTHOR_AZ = ('Author A-Z', 'aaz',
                 f'{Comment.USER_FIELD}__{User.USERNAME_FIELD}')
    AUTHOR_ZA = ('Author Z-A', 'aza',
                 f'-{Comment.USER_FIELD}__{User.USERNAME_FIELD}')
    STATUS_AZ = ('Status A-Z', 'saz',
                 f'{Comment.STATUS_FIELD}__{Status.NAME_FIELD}')
    STATUS_ZA = ('Status Z-A', 'sza',
                 f'-{Comment.STATUS_FIELD}__{Status.NAME_FIELD}')

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg, order)


CommentSortOrder.DEFAULT = CommentSortOrder.OLDEST


class PerPage(ChoiceArg):
    """ Enum representing opinions per page """
    SIX = 6
    NINE = 9
    TWELVE = 12
    FIFTEEN = 15

    def __init__(self, count: int):
        super().__init__(f'{count} per page', count)


PerPage.DEFAULT = PerPage.SIX


def get_query_args(
            request: HttpRequest,
            options: list[tuple[str, Type[ChoiceArg], Any]]
        ) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param options:
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = {}

    for query, clazz, default in options:
        #                value,   was_set
        params[query] = QueryArg(default, False)

        if query in request.GET:
            param = request.GET[query].lower()
            default_value = params[query].query_arg_value
            if isinstance(default_value, int):
                param = int(param)
            if clazz:
                for opt in clazz:
                    if opt.arg == param:
                        params[query].set(opt, True)
                        break
            else:
                params[query].set(param, True)

    return params


# request arguments for an opinion list request
OPINION_LIST_QUERY_ARGS = [
    # query,      arg class,        default value
    (ORDER_QUERY, OpinionSortOrder, OpinionSortOrder.DEFAULT),
    (PAGE_QUERY, None, 1),
    (PER_PAGE_QUERY, PerPage, PerPage.DEFAULT),
    (REORDER_QUERY, None, 0),
    (COMMENT_DEPTH_QUERY, None, DEFAULT_COMMENT_DEPTH),
    (AUTHOR_QUERY, None, None),
    # status included as default is to only show published opinions
    (STATUS_QUERY, QueryStatus, QueryStatus.PUBLISH),
]
# request arguments for an comment list request
COMMENT_LIST_QUERY_ARGS = [
    # query,      arg class,        default value
    (ORDER_QUERY, CommentSortOrder, CommentSortOrder.DEFAULT),
    (PAGE_QUERY, None, 1),
    (PER_PAGE_QUERY, PerPage, PerPage.DEFAULT),
    (REORDER_QUERY, None, 0),
    (COMMENT_DEPTH_QUERY, None, DEFAULT_COMMENT_DEPTH),
    (AUTHOR_QUERY, None, None),
    (OPINION_ID_QUERY, None, None),
    (PARENT_ID_QUERY, None, None),
    # status included as default is to only show published comments
    (STATUS_QUERY, QueryStatus, QueryStatus.PUBLISH),
]
# non-filtering query args, e.g. args for a reorder request etc. which aren't
# included in the query used by the database
REORDER_REQ_QUERY_ARGS = [
    ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, REORDER_QUERY,
    COMMENT_DEPTH_QUERY
]
# query args sent for list request which are not always sent with
# a reorder request
NON_REORDER_OPINION_LIST_QUERY_ARGS = [
    a[0] for a in OPINION_LIST_QUERY_ARGS
    if a[0] not in REORDER_REQ_QUERY_ARGS
]
NON_REORDER_COMMENT_LIST_QUERY_ARGS = [
    a[0] for a in COMMENT_LIST_QUERY_ARGS
    if a[0] not in REORDER_REQ_QUERY_ARGS
]

# date query request arguments for a search request
DATE_QUERY_ARGS = [
    # query,       arg class, default value
    (ON_OR_AFTER_QUERY, None, None),
    (ON_OR_BEFORE_QUERY, None, None),
    (AFTER_QUERY, None, None),
    (BEFORE_QUERY, None, None),
    (EQUAL_QUERY, None, None),
]

# request arguments for an opinion search request
OPTION_SEARCH_QUERY_ARGS = OPINION_LIST_QUERY_ARGS.copy()
OPTION_SEARCH_QUERY_ARGS.extend([
    # query,       arg class, default value
    (SEARCH_QUERY, None, None),
    (TITLE_QUERY, None, None),
    (CONTENT_QUERY, None, None),
    (CATEGORY_QUERY, None, None),
])
OPTION_SEARCH_QUERY_ARGS.extend(DATE_QUERY_ARGS)

# request arguments for a comment search request
COMMENT_SEARCH_QUERY_ARGS = COMMENT_LIST_QUERY_ARGS.copy()
COMMENT_SEARCH_QUERY_ARGS.extend([
    # query,       arg class, default value
    (SEARCH_QUERY, None, None),
    (CONTENT_QUERY, None, None),
])
COMMENT_SEARCH_QUERY_ARGS.extend(DATE_QUERY_ARGS)


def opinion_list_query_args(
            request: HttpRequest
        ) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, OPINION_LIST_QUERY_ARGS)


def opinion_search_query_args(
            request: HttpRequest
        ) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, OPTION_SEARCH_QUERY_ARGS)


def comment_list_query_args(
        request: HttpRequest
) -> dict[str, QueryArg]:
    """
    Get comment list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, COMMENT_LIST_QUERY_ARGS)


def comment_search_query_args(
            request: HttpRequest
        ) -> dict[str, QueryArg]:
    """
    Get comment list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, COMMENT_SEARCH_QUERY_ARGS)


def opinion_permissions(request: HttpRequest) -> dict:
    """
    Get the current user's permissions for Opinions
    :param request: current request
    :return: dict of permissions
    """
    permissions = {}
    for model, check_func in [
        (Opinion._meta.model_name.lower(), opinion_permission_check),
        (Comment._meta.model_name.lower(), comment_permission_check)
    ]:
        permissions.update({
            f'{model}_{op.name.lower()}':
                check_func(request, op, raise_ex=False)
            for op in Crud
        })
    return permissions


def opinion_permission_check(request: HttpRequest, op: Crud,
                             raise_ex: bool = True) -> bool:
    """
    Check request user has specified opinion permission
    :param request: http request
    :param op: Crud operation to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Opinion, op, app_label=OPINIONS_APP_NAME,
                            raise_ex=raise_ex)


def comment_permission_check(request: HttpRequest, op: Crud,
                             raise_ex: bool = True) -> bool:
    """
    Check request user has specified comment permission
    :param request: http request
    :param op: Crud operation to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Comment, op, app_label=OPINIONS_APP_NAME,
                            raise_ex=raise_ex)


def own_opinion_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check request user is opinion author
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id:
        raise PermissionDenied(
            "Opinions may only be updated by their authors")


def published_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check requested opinion is published
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id and \
            opinion_obj.status.name != STATUS_PUBLISHED:
        raise PermissionDenied(
            "Opinion unavailable")


def render_opinion_form(
        title: str, submit_url: str = None, form: OpinionForm = None,
        opinion_obj: Opinion = None, comments: dict = None,
        read_only: bool = False, status: Status = None) -> tuple[
            str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion template
    :param title: title
    :param submit_url: form commit url
    :param form: form to display, default None
    :param opinion_obj: opinion object, default None
    :param comments: details of comments
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    context = get_opinion_context(
        title, submit_url=submit_url, form=form, opinion_obj=opinion_obj,
        comments=comments, read_only=read_only, status=status
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


def generate_excerpt(content: str):
    """
    Generate an excerpt
    :param content: content to generate excerpt from
    :return: excerpt string
    """
    soup = BeautifulSoup(content, features="lxml")
    return truncatechars(
        soup.get_text(), Opinion.OPINION_ATTRIB_EXCERPT_MAX_LEN)
