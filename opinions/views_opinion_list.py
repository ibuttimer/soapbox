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
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse
from django.views import generic

from categories.models import Status, Category
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import Crud, app_template_path
from .comment_data import get_popularity_levels
from .constants import (
    ORDER_QUERY, STATUS_QUERY, PER_PAGE_QUERY, TITLE_QUERY,
    CONTENT_QUERY, CATEGORY_QUERY, AUTHOR_QUERY, ON_OR_AFTER_QUERY,
    ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY, EQUAL_QUERY,
    OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS, SEARCH_QUERY,
    PAGE_QUERY, REORDER_QUERY, ID_FIELD, HIDDEN_QUERY, DATE_NEWEST_LOOKUP,
    DESC_LOOKUP, PINNED_QUERY, TEMPLATE_OPINION_REACTIONS,
    TEMPLATE_REACTION_CTRLS
)
from .models import Opinion, HideStatus, is_id_lookup, PinStatus
from .queries import opinion_is_pinned
from .reactions import OPINION_REACTIONS, get_reaction_status, ReactionsList
from .search import (
    regex_matchers, TERM_GROUP, regex_date_matchers, DATE_QUERY_GROUP,
    DATE_QUERIES, DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
    DATE_QUERY_DAY_GROUP, MARKER_CHARS
)
from .views_utils import (
    opinion_list_query_args, opinion_permission_check,
    opinion_search_query_args,
    REORDER_REQ_QUERY_ARGS,
    NON_REORDER_OPINION_LIST_QUERY_ARGS
)
from .query_params import QuerySetParams, choice_arg_query
from .enums import QueryArg, QueryStatus, OpinionSortOrder, PerPage, Hidden, \
    Pinned, ChoiceArg

NON_DATE_QUERIES = [
    TITLE_QUERY, CONTENT_QUERY, AUTHOR_QUERY, CATEGORY_QUERY, STATUS_QUERY,
    HIDDEN_QUERY, PINNED_QUERY
]
REGEX_MATCHERS = regex_matchers(NON_DATE_QUERIES)
REGEX_MATCHERS.update(regex_date_matchers())

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    STATUS_QUERY: f'{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}',
    TITLE_QUERY: f'{Opinion.TITLE_FIELD}__icontains',
    CONTENT_QUERY: f'{Opinion.CONTENT_FIELD}__icontains',
    AUTHOR_QUERY: f'{Opinion.USER_FIELD}__{User.USERNAME_FIELD}__icontains',
    CATEGORY_QUERY: f'{Opinion.CATEGORIES_FIELD}__in',
    ON_OR_AFTER_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__gte',
    ON_OR_BEFORE_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__lte',
    AFTER_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__gt',
    BEFORE_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__lt',
    EQUAL_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date',
}
# priority order list of query terms
FILTERS_ORDER = [
    # search is a shortcut filter, if search is specified nothing
    # else is checked after
    SEARCH_QUERY,
]
ALWAYS_FILTERS = [
    # always applied items
    STATUS_QUERY, HIDDEN_QUERY
]
FILTERS_ORDER.extend(
    [q for q in FIELD_LOOKUPS if q not in FILTERS_ORDER]
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


class ListTemplate(Enum):
    """ Enum representing possible response template """
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

    user: User
    """ User which initiated request """

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

        self.user = request.user

        # build search term string from values that were set
        self.extra_context = {
            "repeat_search_term": '&'.join([
                f'{q}={v.query_arg_value}'
                for q, v in query_params.items()
                if q not in REORDER_REQ_QUERY_ARGS and v.was_set])
        }

        # select sort order options to display
        self.set_sort_order_options(request, query_params)

        # set queryset
        self.set_queryset(query_params, request.user)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super(OpinionList, self). \
            get(request, *args, **kwargs)

    def set_queryset(self, query_params: dict[str, QueryArg], user: User):
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param user: current user
        """
        query_set_params = QuerySetParams()

        for query in NON_REORDER_OPINION_LIST_QUERY_ARGS:
            get_lookup(query, query_params[query].value, user,
                       query_set_params=query_set_params)

        self.queryset = query_set_params.apply(
            Opinion.objects.prefetch_related('categories'))

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
        order: OpinionSortOrder = query_params[ORDER_QUERY].value
        ordering = [order.order]    # list of lookups
        if order.to_field() != OpinionSortOrder.DEFAULT.to_field():
            # add secondary sort by default sort option
            ordering.append(OpinionSortOrder.DEFAULT.order)
        # published date is only set once opinion is published so apply an
        # additional orderings: by updated and id
        ordering.append(f'{DATE_NEWEST_LOOKUP}{Opinion.UPDATED_FIELD}')
        ordering.append(f'{Opinion.ID_FIELD}')
        self.ordering = tuple(ordering)

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
            def insensitive_order(order: str):
                """ Make text orderings case-insensitive """
                non_text = Opinion.is_date_lookup(order) or is_id_lookup(order)
                return \
                    order if non_text else \
                    Lower(order[1:]).desc() \
                    if order.startswith(DESC_LOOKUP) else Lower(order)
            ordering = tuple(
                map(insensitive_order, ordering))
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

        def is_pinned(opinion: Opinion):
            """ Check if opinion is pinned by current user """
            return opinion_is_pinned(opinion, self.user)

        # initial ordering if secondary sort
        main_order = self.ordering \
            if isinstance(self.ordering, str) else self.ordering[0]
        context.update({
            'sort_order': self.sort_order,
            'selected_sort': list(
                filter(lambda order: order.order == main_order,
                       OpinionSortOrder)
            )[0],
            'per_page': list(PerPage),
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
            ],
            "popularity": get_popularity_levels(context['opinion_list']),
            TEMPLATE_OPINION_REACTIONS: OPINION_REACTIONS,
            TEMPLATE_REACTION_CTRLS: get_reaction_status(
                self.user, list(context['opinion_list']),
                # display pin/unpin
                reactions=ReactionsList.PIN_FIELDS,
                visibility={
                    ReactionsList.PIN_FIELD: is_pinned,
                    ReactionsList.UNPIN_FIELD: is_pinned
                }
            ),
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

        self.user = request.user

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
        self.set_queryset(query_params, request.user)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super(OpinionList, self). \
            get(request, *args, **kwargs)

    def set_queryset(self, query_params: dict[str, QueryArg], user: User):
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param user: current user
        """
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#id4
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups

        query_set_params = QuerySetParams()
        query_entered = False  # query term entered flag

        for key in FILTERS_ORDER:
            value = query_params[key].value
            was_set = query_params[key].was_set

            if value:
                if key in ALWAYS_FILTERS and not was_set:
                    # don't set always applied filter until everything
                    # else is checked
                    continue

                if not query_entered:
                    query_entered = was_set

                get_lookup(key, value, user, query_set_params=query_set_params)

                if key == SEARCH_QUERY and not query_set_params.is_empty:
                    # search is a shortcut filter, if search is specified
                    # nothing else is checked after
                    break

        if not query_entered or not query_set_params.is_empty:
            # no query term entered => all opinions,
            # or query term => search

            for key in ALWAYS_FILTERS:
                if key in query_set_params.params:
                    continue    # always filter was already applied

                value = query_params[key].value
                if value:
                    get_lookup(key, value, user,
                               query_set_params=query_set_params)

            self.queryset = query_set_params.apply(
                Opinion.objects.prefetch_related('categories'))

        else:
            # invalid query term entered
            self.queryset = Opinion.objects.none()


def get_lookup(
            query: str, value: Any, user: User,
            query_set_params: QuerySetParams = None
        ) -> QuerySetParams:
    """
    Get the query lookup for the specified value
    :param query: query argument
    :param value: argument value
    :param user: current user
    :param query_set_params: query set params
    :return: query set params
    """
    if query_set_params is None:
        query_set_params = QuerySetParams()

    if query in [SEARCH_QUERY, CATEGORY_QUERY] or query in DATE_QUERIES:
        query_set_params = get_search_term(
            value, user, query_set_params=query_set_params)
    elif query == STATUS_QUERY:
        if value == QueryStatus.ALL:
            query_set_params.add_all_inclusive(query)
        else:
            query_set_params.add_and_lookup(
                query, FIELD_LOOKUPS[query], value.display)
        # else do not include status in query
    elif query == HIDDEN_QUERY:
        get_hidden_query(query_set_params, value, user)
    elif query == PINNED_QUERY:
        get_pinned_query(query_set_params, value, user)
    elif value:
        query_set_params.add_and_lookup(query, FIELD_LOOKUPS[query], value)

    return query_set_params


def get_search_term(
            value: str, user: User,
            query_set_params: QuerySetParams = None
        ) -> QuerySetParams:
    """
    Generate search terms for specified input value
    :param value: search value
    :param user: current user
    :param query_set_params: query set params
    :return: query set params
    """
    if query_set_params is None:
        query_set_params = QuerySetParams()

    for regex, query, group in SEARCH_REGEX:
        match = regex.match(value)
        if match:
            if query == CATEGORY_QUERY:
                # need inner queryset to get list of categories with names
                # like the search term and then look for opinions with those
                # categories
                # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#icontains
                inner_qs = Category.objects.filter(**{
                    f'{Category.NAME_FIELD}__icontains': match.group(group)
                })
                query_set_params.add_and_lookup(
                    query, FIELD_LOOKUPS[query], inner_qs)
            elif query == STATUS_QUERY:
                # need inner queryset to get list of statuses with names
                # like the search term and then look for opinions with those
                # statuses
                choice_arg_query(
                    query_set_params, match.group(group).lower(),
                    QueryStatus, QueryStatus.ALL,
                    Status, Status.NAME_FIELD, query, FIELD_LOOKUPS[query]
                )
            elif query == HIDDEN_QUERY:
                # need to filter/exclude by list of opinions that the user has
                # hidden
                hidden = Hidden.from_arg(match.group(group).lower())
                get_hidden_query(query_set_params, hidden, user)
            elif query == PINNED_QUERY:
                # need to filter/exclude by list of opinions that the user has
                # pinned
                pinned = Pinned.from_arg(match.group(group).lower())
                get_pinned_query(query_set_params, pinned, user)
            elif query in DATE_QUERIES:
                try:
                    date = datetime(
                        int(match.group(DATE_QUERY_YR_GROUP)),
                        int(match.group(DATE_QUERY_MTH_GROUP)),
                        int(match.group(DATE_QUERY_DAY_GROUP)),
                        tzinfo=ZoneInfo("UTC")
                    )
                    query_set_params.add_and_lookup(
                        query, FIELD_LOOKUPS[query], date)
                except ValueError:
                    # ignore invalid date
                    # TODO add errors to QuerySetParams
                    # so they can be returned to user
                    pass
            else:
                query_set_params.add_and_lookup(
                    query, FIELD_LOOKUPS[query], match.group(group))

    if query_set_params.is_empty:
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
                query_set_params.add_or_lookup(
                    '-'.join(to_query),
                    Q(_connector=Q.OR, **{
                        FIELD_LOOKUPS[q]: term for term in or_q[q]
                    })
                )

    return query_set_params


def get_yes_no_ignore_query(
            query_set_params: QuerySetParams, query: str,
            yes: ChoiceArg, no: ChoiceArg, ignore: ChoiceArg,
            choice: ChoiceArg, clazz: Type[ChoiceArg],
            chosen_qs: QuerySet
        ):
    """
    Get the choice status query
    :param query_set_params: query params to update
    :param query: query term from request
    :param yes: yes choice in ChoiceArg
    :param no: no choice in ChoiceArg
    :param ignore: ignore choice in ChoiceArg
    :param choice: choice from request
    :param clazz: ChoiceArg class
    :param chosen_qs: query to get chosen item from db
    :return: function to apply query
    """
    if choice == ignore:
        query_set_params.add_all_inclusive(query)
    elif isinstance(choice, clazz):
        # get ids of opinions chosen by the user
        query_params = {
            f'{ID_FIELD}__in': chosen_qs
        }

        if choice == no:
            # exclude chosen opinions
            def qs_exclude(qs: QuerySet):
                return qs.exclude(**query_params)
            query_set = qs_exclude
        elif choice == yes:
            # only chosen opinions
            def qs_filter(qs: QuerySet):
                return qs.filter(**query_params)
            query_set = qs_filter
        else:
            query_set = None

        if query_set:
            query_set_params.add_qs_func(query, query_set)


def get_hidden_query(
        query_set_params: QuerySetParams,
        hidden: Hidden, user: User):
    """
    Get the hidden status query
    :param query_set_params: query params to update
    :param hidden: hidden status
    :param user: current user
    :return: function to apply query
    """
    get_yes_no_ignore_query(
        query_set_params, HIDDEN_QUERY, Hidden.YES, Hidden.NO, Hidden.IGNORE,
        hidden, Hidden, HideStatus.objects.filter(**{
            HideStatus.USER_FIELD: user,
            f'{HideStatus.OPINION_FIELD}__isnull': False
        }).values(HideStatus.OPINION_FIELD)
    )


def get_pinned_query(
        query_set_params: QuerySetParams,
        pinned: Pinned, user: User):
    """
    Get the hidden status query
    :param query_set_params: query params to update
    :param pinned: pinned status
    :param user: current user
    :return: function to apply query
    """
    get_yes_no_ignore_query(
        query_set_params, PINNED_QUERY, Pinned.YES, Pinned.NO, Pinned.IGNORE,
        pinned, Pinned, PinStatus.objects.filter(**{
            PinStatus.USER_FIELD: user,
        }).values(PinStatus.OPINION_FIELD)
    )
