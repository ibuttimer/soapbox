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
from http import HTTPStatus
from typing import Any, Type, Union, List, Optional, TypeVar
from zoneinfo import ZoneInfo

from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from django.urls import ResolverMatch

from opinions.queries import is_following
from soapbox import OPINIONS_APP_NAME
from soapbox.constants import (
    OPINION_MENU_CTX, COMMENT_MENU_CTX, MODERATOR_MENU_CTX
)
from utils import (
    Crud, app_template_path, permission_check, find_index, resolve_req
)
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
    ID_QUERY, STATUS_BG_CTX, DELETED_CONTENT_CTX, HIDDEN_CONTENT_CTX,
    DELETED_CONTENT, HIDDEN_COMMENT_CONTENT,
    UNDER_REVIEW_COMMENT_CONTENT, UNDER_REVIEW_TITLE_CTX,
    UNDER_REVIEW_EXCERPT_CTX, UNDER_REVIEW_TITLE, UNDER_REVIEW_EXCERPT,
    UNDER_REVIEW_OPINION_CONTENT, UNDER_REVIEW_COMMENT_CTX,
    UNDER_REVIEW_OPINION_CTX, FILTER_QUERY, REVIEW_QUERY, HTML_CTX, TITLE_CTX,
    REVIEW_FORM_CTX, IS_REVIEW_CTX, REVIEW_BUTTON_CTX, REVIEW_BUTTON_TIPS_CTX,
    COMMENT_FORM_CTX, REFERENCE_QUERY, OPINION_IN_REVIEW_ROUTE_NAME,
    COMMENT_IN_REVIEW_ROUTE_NAME, MODE_QUERY, SINGLE_CONTENT_ROUTE_NAMES
)
from opinions.enums import (
    ChoiceArg, QueryArg, QueryStatus, ReactionStatus, OpinionSortOrder,
    CommentSortOrder, PerPage, Hidden, Pinned, Report, FilterMode, ViewMode
)
from opinions.models import Opinion, Comment, Review
from opinions.forms import OpinionForm, ReviewForm

DEFAULT_COMMENT_DEPTH = 2

STATUS_BADGES = {
    QueryStatus.DRAFT.display: "bg-light text-dark",
    QueryStatus.PUBLISH.display: "bg-success text-white",
    QueryStatus.PREVIEW.display: "bg-secondary text-white",
    QueryStatus.PENDING_REVIEW.display: "bg-warning text-white",
    QueryStatus.UNDER_REVIEW.display: "bg-warning text-white",
    QueryStatus.ACCEPTABLE.display: "bg-danger text-white",
    QueryStatus.UNACCEPTABLE.display: "bg-danger text-white",
    QueryStatus.WITHDRAWN.display: "bg-danger text-white",
}
REVIEW_STATUS_BUTTONS = {
    QueryStatus.ACCEPTABLE.display: "btn btn-outline-success",
    QueryStatus.UNACCEPTABLE.display: "btn btn-outline-danger",
}
REVIEW_STATUS_BUTTON_TOOLTIPS = {
    QueryStatus.ACCEPTABLE.display: "Content acceptable",
    QueryStatus.UNACCEPTABLE.display: "Content needs amending",
}

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeQueryOption = TypeVar("TypeQueryOption", bound="QueryOption")


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
    def of_no_cls_dflt(
            cls: Type[TypeQueryOption], query: str) -> TypeQueryOption:
        """ Get QueryOption with no class or default """
        return cls(query=query, clazz=None, default=None)

    @classmethod
    def of_no_cls(
        cls: Type[TypeQueryOption], query: str, default: Union[ChoiceArg, Any]
    ) -> TypeQueryOption:
        """ Get QueryOption with no class or default """
        return cls(query=query, clazz=None, default=default)


# request arguments with always applied defaults for opinions
OPINION_APPLIED_DEFAULTS_QUERY_ARGS: List[QueryOption] = [
    # status included as default is to only show published opinions
    QueryOption(STATUS_QUERY, QueryStatus, QueryStatus.DEFAULT),
    # hidden included as default is to only show visible opinions
    QueryOption(HIDDEN_QUERY, Hidden, Hidden.DEFAULT),
]
# args for an opinion reorder/next page/etc. request
OPINION_REORDER_QUERY_ARGS = [
    QueryOption(ORDER_QUERY, OpinionSortOrder, OpinionSortOrder.DEFAULT),
    QueryOption.of_no_cls(PAGE_QUERY, 1),
    QueryOption(PER_PAGE_QUERY, PerPage, PerPage.DEFAULT),
    QueryOption.of_no_cls(REORDER_QUERY, 0),
    QueryOption.of_no_cls(COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH),
]
REORDER_REQ_QUERY_ARGS = list(
    map(lambda query_opt: query_opt.query, OPINION_REORDER_QUERY_ARGS)
)
# request arguments for an opinion list request
OPINION_LIST_QUERY_ARGS = OPINION_REORDER_QUERY_ARGS.copy()
OPINION_LIST_QUERY_ARGS.extend([
    # non-reorder query args
    QueryOption.of_no_cls_dflt(AUTHOR_QUERY),
    QueryOption(PINNED_QUERY, Pinned, Pinned.DEFAULT),
])
OPINION_LIST_QUERY_ARGS.extend(OPINION_APPLIED_DEFAULTS_QUERY_ARGS)
# request arguments for followed authors list and followed feed requests
# (replace pinned with filter)
FOLLOWED_OPINION_LIST_QUERY_ARGS = OPINION_LIST_QUERY_ARGS.copy()
find_index(
    FOLLOWED_OPINION_LIST_QUERY_ARGS, PINNED_QUERY,
    mapper=lambda item: item.query,
    replace=QueryOption(FILTER_QUERY, FilterMode, FilterMode.DEFAULT)
)
# request arguments for a category feed request
# (replace pinned with category)
CATEGORY_FEED_QUERY_ARGS = OPINION_LIST_QUERY_ARGS.copy()
find_index(
    CATEGORY_FEED_QUERY_ARGS, PINNED_QUERY,
    mapper=lambda item: item.query,
    replace=QueryOption.of_no_cls_dflt(CATEGORY_QUERY)
)
# request arguments for a review opinions list request
REVIEW_OPINION_LIST_QUERY_ARGS = FOLLOWED_OPINION_LIST_QUERY_ARGS.copy()
REVIEW_OPINION_LIST_QUERY_ARGS.extend([
    # non-reorder query args
    QueryOption(REVIEW_QUERY, QueryStatus, QueryStatus.REVIEW_QUERY_DEFAULT),
])

# request arguments with always applied defaults for comments
COMMENT_APPLIED_DEFAULTS_QUERY_ARGS: List[QueryOption] = [
    # comments only have published or deleted status, both of which are needed
    # (deleted to maintain comment tree structure)
]
# args for a comment reorder/next page/etc. request
COMMENT_REORDER_QUERY_ARGS = [
    QueryOption(ORDER_QUERY, CommentSortOrder, CommentSortOrder.DEFAULT),
    QueryOption.of_no_cls(PAGE_QUERY, 1),
    QueryOption(PER_PAGE_QUERY, PerPage, PerPage.DEFAULT),
    QueryOption.of_no_cls(REORDER_QUERY, 0),
    QueryOption.of_no_cls(COMMENT_DEPTH_QUERY, DEFAULT_COMMENT_DEPTH),
]
assert REORDER_REQ_QUERY_ARGS == list(
    map(lambda query_opt: query_opt.query, COMMENT_REORDER_QUERY_ARGS)
)
# request arguments for an comment list request
COMMENT_LIST_QUERY_ARGS = COMMENT_REORDER_QUERY_ARGS.copy()
COMMENT_LIST_QUERY_ARGS.extend([
    # non-reorder query args
    QueryOption.of_no_cls_dflt(AUTHOR_QUERY),
    QueryOption.of_no_cls(OPINION_ID_QUERY, 0),
    QueryOption.of_no_cls(PARENT_ID_QUERY, 0),
    QueryOption.of_no_cls_dflt(ID_QUERY),
])
COMMENT_LIST_QUERY_ARGS.extend(COMMENT_APPLIED_DEFAULTS_QUERY_ARGS)
# request arguments for a review comments list request
REVIEW_COMMENT_LIST_QUERY_ARGS = COMMENT_LIST_QUERY_ARGS.copy()
REVIEW_COMMENT_LIST_QUERY_ARGS.extend([
    # non-reorder query args
    QueryOption(FILTER_QUERY, FilterMode, FilterMode.DEFAULT),
    QueryOption(REVIEW_QUERY, QueryStatus, QueryStatus.REVIEW_QUERY_DEFAULT),
])

# query args sent for list request which are not always sent with
# a reorder request
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
    QueryOption.of_no_cls_dflt(query) for query in DATE_QUERIES
]

# query terms which only appear in a search
SEARCH_ONLY_QUERIES = [SEARCH_QUERY]
SEARCH_ONLY_QUERIES.extend(DATE_QUERIES)

# request arguments for an opinion search request
OPTION_SEARCH_QUERY_ARGS = OPINION_LIST_QUERY_ARGS.copy()
OPTION_SEARCH_QUERY_ARGS.extend([
    QueryOption.of_no_cls_dflt(query) for query in [
        SEARCH_QUERY, TITLE_QUERY, CONTENT_QUERY, CATEGORY_QUERY
    ]
])
OPTION_SEARCH_QUERY_ARGS.extend(DATE_QUERY_ARGS)

# request arguments for a comment search request
COMMENT_SEARCH_QUERY_ARGS = COMMENT_LIST_QUERY_ARGS.copy()
COMMENT_SEARCH_QUERY_ARGS.extend([
    QueryOption.of_no_cls_dflt(query) for query in [
       SEARCH_QUERY, CONTENT_QUERY
    ]
])
COMMENT_SEARCH_QUERY_ARGS.extend(DATE_QUERY_ARGS)


def get_content_context(title: str, context_form_key: str, **kwargs) -> dict:
    """
    Generate the context for an opinion/comment template
    :param title: title
    :param context_form_key: key for content form
    :param kwargs: context keyword values
        submit_url: form commit url, default None
        opinion_form/comment_form: form to display, default None
        read_only: read only flag, default False
        status: status, default None
        all additional keyword args are copied to context
    :return: context dict
    """
    status = kwargs.get(STATUS_CTX, None)
    if status is None:
        status = STATUS_DRAFT

    context = {
        TITLE_CTX: title,
        READ_ONLY_CTX: kwargs.get(READ_ONLY_CTX, False),
        STATUS_CTX: status,
        STATUS_BG_CTX: STATUS_BADGES.get(status),
    }

    context_form = kwargs.get(context_form_key, None)
    if context_form is not None:
        context[context_form_key] = context_form
        context[SUBMIT_URL_CTX] = kwargs.get(SUBMIT_URL_CTX, None)

    for key, value in kwargs.items():
        # copy other keyword args
        if key not in [
            READ_ONLY_CTX, STATUS_CTX, context_form_key, SUBMIT_URL_CTX
        ]:
            value = kwargs.get(key, None)
            if value is not None:
                context[key] = value

    return context


def get_opinion_context(title: str, **kwargs) -> dict:
    """
    Generate the context for the opinion template
    :param title: title
    :param kwargs: context keyword values
        submit_url: form commit url, default None
        opinion_form/comment_form: form to display, default None
        read_only: read only flag, default False
        status: status, default None
        all additional keyword args are copied to context
    :return: context dict
    """
    return get_content_context(title, OPINION_FORM_CTX, **kwargs)


def get_comment_context(title: str, **kwargs) -> dict:
    """
    Generate the context for the comment template
    :param title: title
    :param kwargs: context keyword values
        submit_url: form commit url, default None
        comment_form: form to display, default None
        read_only: read only flag, default False
        status: status, default None
        all additional keyword args are copied to context
    :return: context dict
    """
    return get_content_context(title, COMMENT_FORM_CTX, **kwargs)


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


def content_save_query_args(
        request: HttpRequest) -> tuple[Status, QueryStatus]:
    """
    Get content save query arguments from request query
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


def follow_query_args(request: HttpRequest) -> ReactionStatus:
    """
    Get follow query arguments from request query
    :param request: http request
    :return: tuple of Status and ReactionStatus
    """
    return query_args_value(
        request, QueryOption(
            STATUS_QUERY, ReactionStatus, ReactionStatus.FOLLOW))


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
    :param request: http request
    :param options: list of possible QueryOption
    :return: dict of key query and value (QueryArg | int | str)
    """
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = {}
    if isinstance(options, QueryOption):
        options = [options]

    for option in options:
        params[option.query] = QueryArg.of(option.default)

        if option.query in request.GET:
            param = request.GET[option.query].lower()

            default_value = params[option.query].value_arg_or_value
            if isinstance(default_value, int):
                param = int(param)  # default is int so param should be too

            if option.clazz:
                choice = list(
                    map(option.clazz.from_arg, param.split())
                ) if isinstance(param, str) and ' ' in param else \
                    option.clazz.from_arg(param)

                params[option.query].set(choice, True)
            else:
                params[option.query].set(param, True)

    return params


def opinion_permissions(request: HttpRequest, context: dict = None) -> dict:
    """
    Get the current user's permissions for Opinions
    :param request: current request
    :param context: context to update; default None
    :return: dict of permissions with
            `<model_name>_<crud_op>` as key and boolean value
    """
    if context is None:
        context = {}
    # permissions for opinion and comment
    for model, check_func in [
        (Opinion, opinion_permission_check),
        (Comment, comment_permission_check),
        (Review, review_permission_check),
    ]:
        context.update({
            f'{model.model_name().lower()}_{crud_op.name.lower()}':
                check_func(request, crud_op, raise_ex=False)
            for crud_op in Crud
        })
        for perm, _ in model._meta.permissions:
            context.update({
                f'{perm}': check_func(request, perm, raise_ex=False)
            })

    return context


MODERATOR_MENU_ROUTES = [
    OPINION_IN_REVIEW_ROUTE_NAME, COMMENT_IN_REVIEW_ROUTE_NAME
]


def _is_moderator_review(request: HttpRequest, route: str):
    """ Check for moderator viewing opinion/comment in review mode """
    return route in SINGLE_CONTENT_ROUTE_NAMES and \
        request.GET.get(MODE_QUERY, None) == ViewMode.REVIEW.arg


def _is_moderator_menu(request: HttpRequest, route: str):
    """ Check if route is a moderator menu route """
    # in review routes follow route prefix convention
    mod_menu = route in MODERATOR_MENU_ROUTES
    if mod_menu:
        # but with an author query they're in opinion/comment menu
        mod_menu = AUTHOR_QUERY not in request.GET
    else:
        # check moderator viewing opinion/comment in review mode
        mod_menu = _is_moderator_review(request, route)
    return mod_menu


def _is_content_menu(request: HttpRequest, route: str, prefix: str):
    """ Check if route is a content menu route """
    # exception to route prefix convention determining menu:
    # - in review routes are in moderator menu, but with an author query
    #   they're in opinion/comment menu
    # - moderator viewing opinion/comment in review mode
    content_menu = \
        route.startswith(prefix) and not _is_moderator_menu(request, route)
    if content_menu:
        # check moderator viewing opinion/comment in review mode
        content_menu = not _is_moderator_review(request, route)
    return content_menu


def add_opinion_context(request: HttpRequest, context: dict = None) -> dict:
    """
    Add opinion-specific context entries
    :param request: current request
    :param context: context to update; default None
    :return: updated context
    """
    if context is None:
        context = {}
    called_by = resolve_req(request)
    if called_by:
        for ctx, check_func in [
            (MODERATOR_MENU_CTX,
             lambda name: _is_moderator_menu(request, name)),
            (OPINION_MENU_CTX,
             lambda name: _is_content_menu(request, name, 'opinion')),
            (COMMENT_MENU_CTX,
             lambda name: _is_content_menu(request, name, 'comment')),
        ]:
            context[ctx] = check_func(called_by.url_name)

    opinion_model_name = Opinion.model_name().lower()
    context.update({
        f'{opinion_model_name}_follow': is_following(request.user).exists()
    })
    return context


def opinion_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified opinion permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Opinion, perm_op,
                            app_label=OPINIONS_APP_NAME, raise_ex=raise_ex)


def comment_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified comment permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Comment, perm_op,
                            app_label=OPINIONS_APP_NAME, raise_ex=raise_ex)


def review_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified review permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Review, perm_op,
                            app_label=OPINIONS_APP_NAME, raise_ex=raise_ex)


def own_content_check(
        request: HttpRequest, content_obj: Union[Opinion, Comment],
        raise_ex: bool = True) -> bool:
    """
    Check request user is content author
    :param request: http request
    :param content_obj: opinion/comment
    :param raise_ex: raise exception if not own; default True
    """
    is_own = request.user.id == content_obj.user.id
    if not is_own and raise_ex:
        raise PermissionDenied(
            f"{content_obj.model_name_caps()}s "
            f"may only be updated by their authors")
    return is_own


def published_check(
        request: HttpRequest, content_obj: Union[Opinion, Comment]):
    """
    Check requested content is published
    :param request: http request
    :param content_obj: opinion/comment
    """
    if request.user.id != content_obj.user.id and \
            content_obj.status.name != STATUS_PUBLISHED:
        raise PermissionDenied(
            f"{content_obj.model_name_caps()} unavailable")


def render_opinion_form(title: str, **kwargs) -> tuple[
            str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion template
    :param title: title
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = get_opinion_context(title, **kwargs)

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


def query_search_term(
    query_params: dict[str, QueryArg], exclude_queries: list[str] = None,
    join_by: str = '&'
) -> str:
    """
    Get the query search terms for a client to use to request
    :param query_params: query params
    :param exclude_queries: list of queries to exclude; default none
    :param join_by: string to join entries; default '&'
    :return: joined sting
    """
    if exclude_queries is None:
        exclude_queries = []

    return join_by.join([
        f'{q}={v.value_arg_or_value if isinstance(v, QueryArg) else v}'
        for q, v in query_params.items()
        if q not in exclude_queries and
        (v.was_set if isinstance(v, QueryArg) else True)])


def add_content_no_show_markers(context: dict = None) -> dict:
    """
    Add the common content can't be shown explanations used in templates
    :param context: context dict to update: default None
    :return: updated/new context dict
    """
    if context is None:
        context = {}
    context.update({
        UNDER_REVIEW_TITLE_CTX: UNDER_REVIEW_TITLE,
        UNDER_REVIEW_EXCERPT_CTX: UNDER_REVIEW_EXCERPT,
        UNDER_REVIEW_COMMENT_CTX: UNDER_REVIEW_COMMENT_CONTENT,
        UNDER_REVIEW_OPINION_CTX: UNDER_REVIEW_OPINION_CONTENT,
        DELETED_CONTENT_CTX: DELETED_CONTENT,
        HIDDEN_CONTENT_CTX: HIDDEN_COMMENT_CONTENT,
    })
    return context


def form_errors_response(
        form: forms.ModelForm, request: HttpRequest = None) -> JsonResponse:
    """
    Get a form errors response
    :param form: processed form
    :param request: request from client; default None
    :return: response
    """
    return JsonResponse({
        HTML_CTX: render_to_string(
            app_template_path(
                "snippet", "form_errors.html"),
            context={
                'form': form,
            },
            request=request),
    }, status=HTTPStatus.BAD_REQUEST)


def add_review_form_context(mode: ViewMode, effective_status: QueryStatus,
                            context: dict = None) -> dict:
    """
    Add the review form context to the specified context.
    :param mode: view mode
    :param effective_status: effective status of content
    :param context: context to update; default None
    :return: updated context
    """
    if context is None:
        context = {}

    is_review = mode == ViewMode.REVIEW
    context[IS_REVIEW_CTX] = is_review
    if is_review:
        context.update({
            REVIEW_FORM_CTX:
                ReviewForm() if effective_status.is_review_wip_status
                else None,
            REVIEW_BUTTON_CTX: REVIEW_STATUS_BUTTONS,
            REVIEW_BUTTON_TIPS_CTX: REVIEW_STATUS_BUTTON_TOOLTIPS,
        })

    return context


def resolve_ref(request: HttpRequest) -> Optional[ResolverMatch]:
    """
    Resolve any `ref` param in a request
    :param request: http request
    :return: resolver match or None
    """
    return resolve_req(request, query=REFERENCE_QUERY)
