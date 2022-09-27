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
import re
from datetime import datetime
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse
from django.views import generic

from categories.models import Status, Category
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import Crud, app_template_path
from .constants import (
    ORDER_QUERY, STATUS_QUERY, PER_PAGE_QUERY, TITLE_QUERY,
    CONTENT_QUERY, CATEGORY_QUERY, AUTHOR_QUERY, ON_OR_AFTER_QUERY,
    ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY, EQUAL_QUERY,
    OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS, SEARCH_QUERY,
    PAGE_QUERY, REORDER_QUERY
)
from .models import Opinion
from .views_utils import (
    opinion_list_query_args, opinion_permission_check, OpinionSortOrder,
    OpinionPerPage, opinion_search_query_args, QueryStatus,
    QueryArg, REORDER_ALWAYS_SENT_QUERY_ARGS, NON_REORDER_LIST_QUERY_ARGS
)

# chars used to delimit queries
MARKER_CHARS = ['=', '"', "'"]

NON_DATE_QUERIES = [
    TITLE_QUERY, CONTENT_QUERY, AUTHOR_QUERY, CATEGORY_QUERY, STATUS_QUERY
]
REGEX_MATCHERS = {
    # match single/double-quoted text after 'xxx:'
    q: re.compile(
        rf'.*{mark}=(?P<quote>[\'\"])(.*?)(?P=quote)\s*.*', re.IGNORECASE)
    for q, mark in [
        # use query term as marker
        (qm, qm) for qm in NON_DATE_QUERIES
    ]
}
TERM_GROUP = 2     # match group of required text of non-date terms

DATE_QUERIES = [
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY
]
DATE_SEP = '-'
SLASH_SEP = '/'
DOT_SEP = '.'
SPACE_SEP = ' '
SEP_REGEX = rf'[{DATE_SEP}{SLASH_SEP}{DOT_SEP}{SPACE_SEP}]'
DMY_REGEX = rf'(\d+)(?P<sep>[-/. ])(\d+)(?P=sep)(\d*)'
REGEX_MATCHERS.update({
    # match single/double-quoted date after 'xxx:'
    q: re.compile(
        rf'.*{mark}=(?P<quote>[\'\"])({DMY_REGEX})(?P=quote)\s*.*',
        re.IGNORECASE)
    for q, mark in [
        # use query term as marker
        (qm, qm) for qm in DATE_QUERIES
    ]
})
DATE_QUERY_GROUP = 2         # match group of required text
DATE_QUERY_DAY_GROUP = 3     # match group of day text
DATE_QUERY_MTH_GROUP = 5     # match group of month text
DATE_QUERY_YR_GROUP = 6      # match group of year text

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    STATUS_QUERY: f'{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}',
    TITLE_QUERY: f'{Opinion.TITLE_FIELD}__icontains',
    CONTENT_QUERY: f'{Opinion.CONTENT_FIELD}__icontains',
    AUTHOR_QUERY: f'{Opinion.USER_FIELD}__{User.USERNAME_FIELD}__icontains',
    CATEGORY_QUERY: f'{Opinion.CATEGORIES_FIELD}__in',
    # TODO search published date or updated date?
    ON_OR_AFTER_QUERY: f'{Opinion.PUBLISHED_FIELD}__date__gte',
    ON_OR_BEFORE_QUERY: f'{Opinion.PUBLISHED_FIELD}__date__lte',
    AFTER_QUERY: f'{Opinion.PUBLISHED_FIELD}__date__gt',
    BEFORE_QUERY: f'{Opinion.PUBLISHED_FIELD}__date__lt',
    EQUAL_QUERY: f'{Opinion.PUBLISHED_FIELD}__date',
}
# priority order list of query terms
FILTERS_ORDER = [
    # search is a shortcut filter, if search is specified nothing
    # else is checked after
    SEARCH_QUERY,
]
ALWAYS_FILTERS = [
    # always applied items
    STATUS_QUERY,
]
FILTERS_ORDER.extend(
    [q for q in FIELD_LOOKUPS.keys() if q not in FILTERS_ORDER]
)

SEARCH_REGEX = [
    # regex,            query param, regex match group
    (REGEX_MATCHERS[q], q,           TERM_GROUP)
    for q in NON_DATE_QUERIES
]
SEARCH_REGEX.extend([
    # regex,            query param, regex match group
    (REGEX_MATCHERS[q], q,           DATE_QUERY_GROUP)
    for q in DATE_QUERIES
])

REORDER_QUERIES = [ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY]


class ListTemplate(Enum):
    FULL_TEMPLATE = app_template_path(OPINIONS_APP_NAME, 'opinion_list.html')
    CONTENT_TEMPLATE = app_template_path(OPINIONS_APP_NAME,
                                         'opinion_list_content.html')


class OpinionList(LoginRequiredMixin, generic.ListView):
    """
    Opinion list response
    """
    model = Opinion

    response_template: ListTemplate
    """ Response template to use """

    sort_order: list[OpinionSortOrder]
    """ Sort order options to display """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_permission_check(request, Crud.READ)

        # TODO currently '/"/= can't be used in title/content
        # as search depends on them
        query_params = opinion_list_query_args(request)

        # build search term string from values that were set
        self.extra_context = {
            "repeat_search_term": '&'.join([
                f'{q}={v.query_arg_value}'
                for q, v in query_params.items()
                if q not in REORDER_ALWAYS_SENT_QUERY_ARGS and v.was_set])
        }

        # select sort order options to display
        self.set_sort_order_options(request, query_params)

        # set queryset
        self.set_queryset(query_params)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super(OpinionList, self). \
            get(request, *args, **kwargs)

    def set_queryset(self, query_params: dict[str, QueryArg]):
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        """
        and_lookups = {}
        for query in NON_REORDER_LIST_QUERY_ARGS:
            _, ands, _ = get_lookup(query, query_params[query].value)
            and_lookups.update(ands)

        self.queryset = Opinion.objects. \
            prefetch_related('categories'). \
            filter(**and_lookups)

    def set_sort_order_options(self, request: HttpRequest,
                               query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param request: http request
        :param query_params: request query
        :return:
        """
        # select sort order options to display
        excludes = []
        if query_params[AUTHOR_QUERY].was_set_to(request.user.username):
            # no need for sort by author if only one author
            excludes.extend([
                OpinionSortOrder.AUTHOR_AZ, OpinionSortOrder.AUTHOR_ZA
            ])
        if not query_params[STATUS_QUERY].value == QueryStatus.ALL:
            # no need for sort by status if only one status
            excludes.extend([
                OpinionSortOrder.STATUS_AZ, OpinionSortOrder.STATUS_ZA
            ])
        self.sort_order = [
            so for so in OpinionSortOrder if so not in excludes
        ]

    def set_ordering(self, query_params: dict[str, QueryArg]):
        """
        Set the ordering for the response
        :param query_params: request query
        """
        # set ordering
        order = query_params[ORDER_QUERY].value
        ordering = order.order
        if order not in [OpinionSortOrder.NEWEST, OpinionSortOrder.OLDEST]:
            # secondary sort by newest
            ordering = (ordering, OpinionSortOrder.NEWEST.order)
        self.ordering = ordering

    def set_pagination(
            self, query_params: dict[str, QueryArg]):
        """
        Set pagination for the response
        :param query_params: request query
        """
        # set pagination
        self.paginate_by = query_params[PER_PAGE_QUERY].query_arg_value

    def select_template(
            self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        reorder_query = query_params[REORDER_QUERY].value \
            if REORDER_QUERY in query_params else False
        self.response_template = ListTemplate.CONTENT_TEMPLATE \
            if reorder_query else ListTemplate.FULL_TEMPLATE

        self.template_name = self.response_template.value

    def get_ordering(self):
        """ Get ordering of list """
        ordering = self.ordering
        if isinstance(ordering, tuple):
            # make primary sort case-insensitive
            # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#django.db.models.query.QuerySet.order_by
            order_list = list(ordering)
            order_list[0] = Lower(order_list[0][1:]).desc() \
                if order_list[0].startswith('-') else Lower(order_list[0])
            ordering = tuple(order_list)
        return ordering

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """
        Get template context
        :param object_list:
        :param kwargs: additional keyword arguments
        :return:
        """
        context = super(OpinionList, self).\
            get_context_data(object_list=object_list, **kwargs)

        # initial ordering if secondary sort
        main_order = self.ordering \
            if isinstance(self.ordering, str) else self.ordering[0]
        context.update({
            'sort_order': self.sort_order,
            'selected_sort': list(
                filter(lambda order: order.order == main_order,
                       OpinionSortOrder)
            )[0],
            'per_page': list(OpinionPerPage),
            'selected_per_page': self.paginate_by,
            'page_range': [{
                'page_num': page,
                'disabled': page == Paginator.ELLIPSIS,
                'href':
                    f"?page={page}" if page != Paginator.ELLIPSIS else '#',
                'label':
                    f"page {page}" if page != Paginator.ELLIPSIS else '',
                'hidden': f'{bool(page != Paginator.ELLIPSIS)}',
            } for page in context['paginator'].get_elided_page_range(
                number=context['page_obj'].number,
                on_each_side=OPINION_PAGINATION_ON_EACH_SIDE,
                on_ends=OPINION_PAGINATION_ON_ENDS)
            ]
        })

        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        # return 204 for no content
        if self.response_template == ListTemplate.CONTENT_TEMPLATE and \
                len(context['object_list']) == 0:
            response_kwargs['status'] = HTTPStatus.NO_CONTENT

        return super(OpinionList, self).render_to_response(
            context, **response_kwargs)


class OpinionSearch(OpinionList):
    """
    Search Opinion list response
    """

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        GET method for Opinion search list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        opinion_permission_check(request, Crud.READ)

        # Note: values must be in quotes for search query
        query_params = opinion_search_query_args(request)

        # build search term string from values that were set
        self.extra_context = {
            "search_term": ', '.join([
                f'{q}: {v.value}'
                for q, v in query_params.items() if v.was_set
            ]),
            "repeat_search_term":
                f'{SEARCH_QUERY}='
                f'{query_params[SEARCH_QUERY].value}'
        }

        # select sort order options to display
        self.set_sort_order_options(request, query_params)

        # set the query
        self.set_queryset(query_params)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super(OpinionList, self). \
            get(request, *args, **kwargs)

    def set_queryset(self, query_params: dict[str, QueryArg]):
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        """
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#id4
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups

        and_lookups = {}
        or_lookups = []
        query_entered = False  # query term entered flag

        applied = {}

        for key in FILTERS_ORDER:
            value = query_params[key].value
            was_set = query_params[key].was_set
            applied[key] = was_set

            if value:
                if key in ALWAYS_FILTERS and not was_set:
                    # don't set always applied filter until everything
                    # else is checked
                    continue

                if not query_entered:
                    query_entered = was_set

                terms, ands, ors = get_lookup(key, value)
                if terms:
                    and_lookups.update(ands)
                    or_lookups.extend(ors)

                if key == SEARCH_QUERY and terms:
                    # search is a shortcut filter, if search is specified
                    # nothing else is checked after
                    break

        if not query_entered or len(and_lookups) > 0 or len(or_lookups) > 0:
            # no query term entered => all opinions,
            # or query term => search

            for key in ALWAYS_FILTERS:
                if applied.get(key, False):
                    continue

                value = query_params[key].value
                if value:
                    terms, ands, ors = get_lookup(key, value)
                    if terms:
                        and_lookups.update(ands)
                        or_lookups.extend(ors)

            # OR queries of title and content contains terms
            # (if no specific search terms specified)
            # e.g. "term" =>
            #  "WHERE ( ("title") LIKE '<term>' OR ("content") LIKE '<term>')"
            # AND queries of specific search terms
            # e.g. 'title="term"' =>
            #  "WHERE ("title") LIKE '<term>'"
            self.queryset = Opinion.objects. \
                prefetch_related('categories'). \
                filter(
                    Q(_connector=Q.OR, *or_lookups), **and_lookups)
        else:
            # invalid query term entered
            self.queryset = Opinion.objects.none()


def get_lookup(
            query: str, value: Any
        ) -> tuple[bool, dict[Any, Any], list[Any]]:
    """
    Get the query lookup for the specified
    :param query: query argument
    :param value: argument value
    :return: tuple of AND lookups and OR lookups
    """
    and_lookups = {}
    or_lookups = []

    if query in [SEARCH_QUERY, CATEGORY_QUERY] or query in DATE_QUERIES:
        terms, ands, ors = get_search_term(value)
        if terms:
            and_lookups.update(ands)
            or_lookups.extend(ors)
    elif query == STATUS_QUERY:
        if value != QueryStatus.ALL:
            and_lookups[
                FIELD_LOOKUPS[query]] = value.display
        # else do not include status in query
    elif value:
        and_lookups[
            FIELD_LOOKUPS[query]] = value

    return \
        len(and_lookups) > 0 or len(or_lookups) > 0, and_lookups, or_lookups


def get_search_term(value: str) -> tuple[bool, dict, list]:
    """
    Generate search terms for specified input value
    :param value:
    :return: tuple of
                have terms flag: True when have a search term
                AND search terms: dict of terms to be ANDed together
                OR search terms: list of terms to be ORed together
    """
    and_lookups = {}
    or_lookups = []

    for regex, query, group in SEARCH_REGEX:
        match = regex.match(value)
        if match:
            if query == CATEGORY_QUERY:
                # need inner queryset to get list of categories with names
                # like the search term and then look for opinions with those
                # categories
                # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#in
                inner_qs = Category.objects.filter(**{
                    f'{Category.NAME_FIELD}__icontains': match.group(group)
                })
                and_lookups[FIELD_LOOKUPS[query]] = inner_qs
            elif query == STATUS_QUERY:
                # need inner queryset to get list of statuses with names
                # like the search term and then look for opinions with those
                # statuses
                # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#in
                inner_qs = Status.objects.filter(**{
                    f'{Status.NAME_FIELD}__icontains': match.group(group)
                })
                and_lookups[FIELD_LOOKUPS[query]] = inner_qs
            elif query in DATE_QUERIES:
                try:
                    date = datetime(
                        int(match.group(DATE_QUERY_YR_GROUP)),
                        int(match.group(DATE_QUERY_MTH_GROUP)),
                        int(match.group(DATE_QUERY_DAY_GROUP)),
                        tzinfo=ZoneInfo("UTC")
                    )
                    and_lookups[FIELD_LOOKUPS[query]] = date
                except ValueError:
                    # ignore invalid date
                    pass
            else:
                and_lookups[FIELD_LOOKUPS[query]] = match.group(group)

    if len(and_lookups) == 0:
        if not any(
                list(
                    map(lambda x: x in value, MARKER_CHARS)
                )
        ):
            # no delimiting chars, so search title & content for
            # any of the search terms
            to_query = [TITLE_QUERY, CONTENT_QUERY]
            or_q = {}
            for term in value.split():
                if len(or_q) == 0:
                    or_q = {q: [term] for q in to_query}
                else:
                    or_q[TITLE_QUERY].append(term)
                    or_q[CONTENT_QUERY].append(term)

            # https://docs.djangoproject.com/en/4.1/topics/db/queries/#complex-lookups-with-q

            # OR queries of title and content contains terms
            # e.g. [
            #   "WHERE ("title") LIKE '<term>'",
            #   "WHERE ("content") LIKE '<term>'"
            # ]
            for q in to_query:
                or_lookups.append(
                    Q(_connector=Q.OR, **{FIELD_LOOKUPS[q]: term
                                          for term in or_q[q]})
                )

    return \
        len(and_lookups) > 0 or len(or_lookups) > 0, and_lookups, or_lookups
