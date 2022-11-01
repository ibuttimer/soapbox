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
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Type, Union, List, Optional, TypeVar
from zoneinfo import ZoneInfo

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.template.defaultfilters import truncatechars
from bs4 import BeautifulSoup

from soapbox import OPINIONS_APP_NAME
from utils import Crud, app_template_path, permission_check
from categories import (
    STATUS_DRAFT, STATUS_PUBLISHED, CATEGORY_UNASSIGNED
)
from categories.models import Status, Category
from opinions.constants import (
    ORDER_QUERY, SEARCH_QUERY, STATUS_QUERY, PER_PAGE_QUERY,
    PAGE_QUERY, TITLE_QUERY, CONTENT_QUERY, CATEGORY_QUERY, AUTHOR_QUERY,
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY, REORDER_QUERY, OPINION_ID_QUERY, PARENT_ID_QUERY,
    COMMENT_DEPTH_QUERY, HIDDEN_QUERY, PINNED_QUERY,
    SUBMIT_URL_CTX, READ_ONLY_CTX, STATUS_CTX, OPINION_CTX, OPINION_FORM_CTX,
    ID_QUERY
)
from opinions.enums import (
    ChoiceArg, QueryArg, QueryStatus, ReactionStatus, OpinionSortOrder,
    CommentSortOrder, PerPage, Hidden, Pinned, Report
)
from opinions.models import Opinion, Comment
from opinions.forms import OpinionForm

DEFAULT_COMMENT_DEPTH = 2

# workaround for self type hints from https://peps.python.org/pep-0673/
TQueryOption = TypeVar("TQueryOption", bound="QueryOption")


@dataclass
class QueryOption:
    """
    Request query option class
    """
    query: str
    """ Query key """
    clazz: Optional[Type[ChoiceArg]]
    """ Class of choice result """
    default: Union[ChoiceArg, Any]
    """ Default choice """

    @classmethod
    def of_no_cls_dflt(cls: Type[TQueryOption], query: str) -> TQueryOption:
        """ Get QueryOption with no class or default """
        return cls(query=query, clazz=None, default=None)

    @classmethod
    def of_no_cls(
        cls: Type[TQueryOption], query: str, default: Union[ChoiceArg, Any]
    ) -> TQueryOption:
        """ Get QueryOption with no class or default """
        return cls(query=query, clazz=None, default=default)


# request arguments with always applied defaults
APPLIED_DEFAULTS_QUERY_ARGS = [
    # query,      arg class,        default value
    # status included as default is to only show published opinions
    QueryOption(STATUS_QUERY, QueryStatus, QueryStatus.PUBLISH),
    # hidden included as default is to only show visible opinions
    QueryOption(HIDDEN_QUERY, Hidden, Hidden.DEFAULT),
]
# request arguments for an opinion list request
OPINION_LIST_QUERY_ARGS = [
    # query,      arg class,        default value
    QueryOption(ORDER_QUERY, OpinionSortOrder, OpinionSortOrder.DEFAULT),
    QueryOption.of_no_cls(PAGE_QUERY, 1),
    QueryOption(PER_PAGE_QUERY, PerPage, PerPage.DEFAULT),
    QueryOption.of_no_cls(REORDER_QUERY, 0),
    QueryOption.of_no_cls(COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH),
    # non-reorder query args
    QueryOption.of_no_cls_dflt(AUTHOR_QUERY),
    QueryOption(PINNED_QUERY, Pinned, Pinned.IGNORE),
]
OPINION_LIST_QUERY_ARGS.extend(APPLIED_DEFAULTS_QUERY_ARGS)
# request arguments for an comment list request
COMMENT_LIST_QUERY_ARGS = [
    # query,      arg class,        default value
    QueryOption(ORDER_QUERY, CommentSortOrder, CommentSortOrder.DEFAULT),
    QueryOption.of_no_cls(PAGE_QUERY, 1),
    QueryOption(PER_PAGE_QUERY, PerPage, PerPage.DEFAULT),
    QueryOption.of_no_cls(REORDER_QUERY, 0),
    QueryOption.of_no_cls(COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH),
    # non-reorder query args
    QueryOption.of_no_cls_dflt(AUTHOR_QUERY),
    QueryOption.of_no_cls_dflt(OPINION_ID_QUERY),
    QueryOption.of_no_cls_dflt(PARENT_ID_QUERY),
    QueryOption.of_no_cls_dflt(ID_QUERY),
]
COMMENT_LIST_QUERY_ARGS.extend(APPLIED_DEFAULTS_QUERY_ARGS)
# args for a reorder/next page/etc. request
REORDER_REQ_QUERY_ARGS = [
    ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, REORDER_QUERY,
    COMMENT_DEPTH_QUERY
]
# query args sent for list request which are not always sent with
# a reorder request
NON_REORDER_OPINION_LIST_QUERY_ARGS = [
    a.query for a in OPINION_LIST_QUERY_ARGS
    if a.query not in REORDER_REQ_QUERY_ARGS
]
NON_REORDER_COMMENT_LIST_QUERY_ARGS = [
    a.query for a in COMMENT_LIST_QUERY_ARGS
    if a.query not in REORDER_REQ_QUERY_ARGS
]

DATE_QUERIES = [
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY
]
# date query request arguments for a search request
DATE_QUERY_ARGS = [
    # query,       arg class, default value
    QueryOption.of_no_cls_dflt(query) for query in DATE_QUERIES
]

# request arguments for an opinion search request
OPTION_SEARCH_QUERY_ARGS = OPINION_LIST_QUERY_ARGS.copy()
OPTION_SEARCH_QUERY_ARGS.extend([
    # query,       arg class, default value
    QueryOption.of_no_cls_dflt(query) for query in [
        SEARCH_QUERY, TITLE_QUERY, CONTENT_QUERY, CATEGORY_QUERY
    ]
])
OPTION_SEARCH_QUERY_ARGS.extend(DATE_QUERY_ARGS)

# request arguments for a comment search request
COMMENT_SEARCH_QUERY_ARGS = COMMENT_LIST_QUERY_ARGS.copy()
COMMENT_SEARCH_QUERY_ARGS.extend([
    # query,       arg class, default value
    QueryOption.of_no_cls_dflt(query) for query in [
       SEARCH_QUERY, CONTENT_QUERY
    ]
])
COMMENT_SEARCH_QUERY_ARGS.extend(DATE_QUERY_ARGS)


def get_opinion_context(title: str, **kwargs) -> dict:
    """
    Generate the context for the opinion template
    :param title: title
    :param kwargs: context keyword values
        comment_submit_url: form commit url, default None
        comment_form: form to display, default None
        opinion: opinion object, default None
        comments: details of comments
        read_only: read only flag, default False
        status: status, default None
    :return: tuple of template path and context
    """
    status = kwargs.get(STATUS_CTX, None)
    if status is None:
        status = STATUS_DRAFT

    status_text = status if isinstance(status, str) else status.name

    context = {
        'title': title,
        READ_ONLY_CTX: kwargs.get(READ_ONLY_CTX, False),
        STATUS_CTX: status_text,
        'status_bg':
            'bg-primary' if status_text == STATUS_DRAFT else 'bg-success',
    }

    opinion_form = kwargs.get(OPINION_FORM_CTX, None)
    if opinion_form is not None:
        context[OPINION_FORM_CTX] = opinion_form
        context[SUBMIT_URL_CTX] = kwargs.get(SUBMIT_URL_CTX, None)

    for key, value in kwargs.items():
        if key not in [
            READ_ONLY_CTX, STATUS_CTX, OPINION_FORM_CTX, SUBMIT_URL_CTX
        ]:
            value = kwargs.get(key, None)
            if value is not None:
                context[key] = value

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


def query_args_value(
        request: HttpRequest, query_option: QueryOption) -> Type[ChoiceArg]:
    """
    Get query arguments from request query
    :param request: http request
    :param query_option: query option
    :return: argument class instance
    """
    # query params are in request.GET
    # maybe slightly unorthodox, but saves defining 3 routes
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = get_query_args(request, query_option)
    status_query = params[query_option.query].value

    return status_query


def query_args_status(
    request: HttpRequest, query_option: QueryOption
) -> tuple[Status, Type[ChoiceArg]]:
    """
    Get query arguments from request query
    :param request: http request
    :param query_option: query option
    :return: tuple of Status and argument class instance
    """
    status_query = query_args_value(request, query_option)
    status = Status.objects.get(name=status_query.display)

    return status, status_query


def opinion_save_query_args(
        request: HttpRequest) -> tuple[Status, QueryStatus]:
    """
    Get opinion save query arguments from request query
    :param request: http request
    :return: tuple of Status and QueryStatus
    """
    return query_args_status(
        request, QueryOption(STATUS_QUERY, QueryStatus, QueryStatus.DRAFT))


def like_query_args(
        request: HttpRequest) -> tuple[Status, ReactionStatus]:
    """
    Get like query arguments from request query
    :param request: http request
    :return: tuple of Status and ReactionStatus
    """
    return query_args_status(
        request, QueryOption(
            STATUS_QUERY, ReactionStatus, ReactionStatus.AGREE))


def pin_query_args(request: HttpRequest) -> ReactionStatus:
    """
    Get pin query arguments from request query
    :param request: http request
    :return: tuple of Status and ReactionStatus
    """
    return query_args_value(
        request, QueryOption(
            STATUS_QUERY, ReactionStatus, ReactionStatus.PIN))


def hide_query_args(request: HttpRequest) -> ReactionStatus:
    """
    Get hide query arguments from request query
    :param request: http request
    :return: tuple of Status and ReactionStatus
    """
    return query_args_value(
        request, QueryOption(
            STATUS_QUERY, ReactionStatus, ReactionStatus.HIDE))


def report_query_args(request: HttpRequest) -> Report:
    """
    Get report query arguments from request query
    :param request: http request
    :return: tuple of Status and Report
    """
    return query_args_value(
        request, QueryOption(STATUS_QUERY, Report, Report.DEFAULT))


def get_query_args(
            request: HttpRequest,
            options: Union[QueryOption, List[QueryOption]]
        ) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param options: list of possible QueryOption
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = {}
    if isinstance(options, QueryOption):
        options = [options]

    for option in options:
        #                               value,   was_set
        params[option.query] = QueryArg(option.default, False)

        if option.query in request.GET:
            param = request.GET[option.query].lower()
            default_value = params[option.query].query_arg_value
            if isinstance(default_value, int):
                param = int(param)
            if option.clazz:
                for opt in option.clazz:
                    if opt.arg == param:
                        params[option.query].set(opt, True)
                        break
            else:
                params[option.query].set(param, True)

    return params


def opinion_list_query_args(request: HttpRequest) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, OPINION_LIST_QUERY_ARGS)


def opinion_search_query_args(request: HttpRequest) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, OPTION_SEARCH_QUERY_ARGS)


def comment_list_query_args(request: HttpRequest) -> dict[str, QueryArg]:
    """
    Get comment list query arguments from request query
    :param request: http request
    :return: dict of tuples of value (ChoiceArg | int | str) and
            'was set' bool flag
    """
    return get_query_args(request, COMMENT_LIST_QUERY_ARGS)


def comment_search_query_args(request: HttpRequest) -> dict[str, QueryArg]:
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


def own_opinion_check(request: HttpRequest, opinion_obj: Opinion,
                      raise_ex: bool = True) -> bool:
    """
    Check request user is opinion author
    :param request: http request
    :param opinion_obj: opinion
    :param raise_ex: raise exception if not own; default True
    """
    is_own = request.user.id == opinion_obj.user.id
    if not is_own and raise_ex:
        raise PermissionDenied(
            "Opinions may only be updated by their authors")
    return is_own


def published_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check requested opinion is published
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id and \
            opinion_obj.status.name != STATUS_PUBLISHED:
        raise PermissionDenied("Opinion unavailable")


def render_opinion_form(title: str, **kwargs) -> tuple[
            str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion template
    :param title: title
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = get_opinion_context(title, **kwargs)

    context.update({
        'summernote_fields': [OpinionForm.CONTENT_FF],
        'other_fields': [OpinionForm.TITLE_FF],
        'category_fields': [OpinionForm.CATEGORIES_FF],
    })

    # set initial data
    opinion_form = context.get(OPINION_FORM_CTX, None)
    if opinion_form:
        opinion_obj = context.get(OPINION_CTX, None)
        opinion_form[OpinionForm.CATEGORIES_FF].initial = [
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


def ensure_list(item: Any) -> list[Any]:
    """
    Ensure argument is returned as a list
    :param item: item(s) to return as list
    :return: list
    """
    return item if isinstance(item, list) else [item]
