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
from typing import Any, Type
from zoneinfo import ZoneInfo

from django.db.models import Q, QuerySet

from categories.models import Status, Category
from opinions.constants import (
    TITLE_QUERY, CONTENT_QUERY, AUTHOR_QUERY, CATEGORY_QUERY, STATUS_QUERY,
    HIDDEN_QUERY, PINNED_QUERY, SEARCH_QUERY, ON_OR_AFTER_QUERY,
    ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY, EQUAL_QUERY, FILTER_QUERY,
    REVIEW_QUERY
)
from opinions.enums import QueryStatus, Hidden, Pinned, ChoiceArg
from opinions.models import Opinion, HideStatus, PinStatus
from opinions.query_params import QuerySetParams, choice_arg_query
from opinions.search import (
    regex_matchers, TERM_GROUP, DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
    DATE_QUERY_DAY_GROUP, MARKER_CHARS, DATE_QUERY_GROUP, regex_date_matchers,
    KEY_TERM_GROUP, DATE_KEY_TERM_GROUP
)
from opinions.views.utils import (
    DATE_QUERIES, SEARCH_ONLY_QUERIES, OPINION_APPLIED_DEFAULTS_QUERY_ARGS
)
from user.models import User
from utils import ensure_list

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
    option.query for option in OPINION_APPLIED_DEFAULTS_QUERY_ARGS
]
FILTERS_ORDER.extend(
    [q for q in FIELD_LOOKUPS if q not in FILTERS_ORDER]
)
# complex queries which require more than a simple lookup
NON_LOOKUP_ARGS = [
    FILTER_QUERY, REVIEW_QUERY
]

SEARCH_REGEX = [
    # regex,            query param, regex match group, key & regex match grp
    (REGEX_MATCHERS[q], q,           TERM_GROUP,        KEY_TERM_GROUP)
    for q in NON_DATE_QUERIES
]
SEARCH_REGEX.extend([
    # regex,            query param, regex match group, key & regex match grp
    (REGEX_MATCHERS[q], q,           DATE_QUERY_GROUP,  DATE_KEY_TERM_GROUP)
    for q in DATE_QUERIES
])


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
    if not value:
        return query_set_params

    if query in SEARCH_ONLY_QUERIES:
        query_set_params = get_search_term(
            value, user, query_set_params=query_set_params)
    elif query == STATUS_QUERY:
        if value == QueryStatus.ALL:
            query_set_params.add_all_inclusive(query)
        elif isinstance(value, list):
            # multi-status search
            query_set_params.add_or_lookup(
                query,
                Q(_connector=Q.OR, *[
                    Q(**{f'{FIELD_LOOKUPS[query]}': stat.display})
                    for stat in value if stat
                ])
            )
        else:
            query_set_params.add_and_lookup(
                query, FIELD_LOOKUPS[query], value.display)
        # else do not include status in query
    elif query == CATEGORY_QUERY:
        get_category_query(query_set_params, value)
    elif query == HIDDEN_QUERY:
        get_hidden_query(query_set_params, value, user)
    elif query == PINNED_QUERY:
        get_pinned_query(query_set_params, value, user)
    elif query not in NON_LOOKUP_ARGS and value:
        query_set_params.add_and_lookup(query, FIELD_LOOKUPS[query], value)
    # else no value or complex query term handled elsewhere

    return query_set_params


def get_search_term(
    value: str, user: User, query_set_params: QuerySetParams = None
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
    if value is None:
        return query_set_params

    for regex, query, group, key_val_group in SEARCH_REGEX:
        match = regex.match(value)
        if match:
            success = True
            if query == CATEGORY_QUERY:
                # need inner queryset to get list of categories with names
                # like the search term and then look for opinions with those
                # categories
                get_category_query(query_set_params, match.group(group))
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
                success = get_hidden_query(query_set_params, hidden, user)
            elif query == PINNED_QUERY:
                # need to filter/exclude by list of opinions that the user has
                # pinned
                pinned = Pinned.from_arg(match.group(group).lower())
                success = get_pinned_query(query_set_params, pinned, user)
            elif query in DATE_QUERIES:
                success = get_date_query(query_set_params, query, *[
                    match.group(idx) for idx in [
                        DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
                        DATE_QUERY_DAY_GROUP
                    ]
                ])
            elif query not in NON_LOOKUP_ARGS:
                query_set_params.add_and_lookup(
                    query, FIELD_LOOKUPS[query], match.group(group))
            else:
                # complex query term handled elsewhere
                success = False

            save_term_func = query_set_params.add_search_term if success \
                else query_set_params.add_invalid_term
            save_term_func(match.group(key_val_group))

    if query_set_params.is_empty and value:
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
            for qry in to_query:
                query_set_params.add_or_lookup(
                    '-'.join(to_query),
                    Q(_connector=Q.OR, **{
                        FIELD_LOOKUPS[qry]: term for term in or_q[qry]
                    })
                )

    return query_set_params


def get_yes_no_ignore_query(
            query_set_params: QuerySetParams, query: str,
            yes_choice: [ChoiceArg, list[ChoiceArg]],
            no_choice: [ChoiceArg, list[ChoiceArg]],
            ignore: [ChoiceArg, list[ChoiceArg]],
            choice: ChoiceArg, clazz: Type[ChoiceArg],
            chosen_qs: QuerySet
        ) -> bool:
    """
    Get a choice status query
    :param query_set_params: query params to update
    :param query: query term from request
    :param yes_choice: yes_choice choice in ChoiceArg
    :param no_choice: no choice in ChoiceArg
    :param ignore: ignore choice in ChoiceArg
    :param choice: choice from request
    :param clazz: ChoiceArg class
    :param chosen_qs: query to get chosen item from db
    :return: True if successfully added
    """
    success = True
    if choice in ensure_list(ignore):
        query_set_params.add_all_inclusive(query)
    elif isinstance(choice, clazz):
        # get ids of opinions chosen by the user
        query_params = {
            f'{Opinion.id_field()}__in': chosen_qs
        }

        if choice in ensure_list(no_choice):
            # exclude chosen opinions
            def qs_exclude(qry_set: QuerySet) -> QuerySet:
                return qry_set.exclude(**query_params)
            query_set = qs_exclude
        elif choice in ensure_list(yes_choice):
            # only chosen opinions
            def qs_filter(qry_set: QuerySet) -> QuerySet:
                return qry_set.filter(**query_params)
            query_set = qs_filter
        else:
            query_set = None

        if query_set:
            query_set_params.add_qs_func(query, query_set)
        else:
            success = False

    return success


def get_category_query(query_set_params: QuerySetParams,
                       name: str) -> None:
    """
    Get the category query
    :param query_set_params: query params to update
    :param name: category name or part thereof
    """
    # need inner queryset to get list of categories with names
    # like the search term and then look for opinions with those
    # categories
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#icontains
    inner_qs = Category.objects.filter(**{
        f'{Category.NAME_FIELD}__icontains': name
    })
    query_set_params.add_and_lookup(
        CATEGORY_QUERY, FIELD_LOOKUPS[CATEGORY_QUERY], inner_qs)


def get_date_query(query_set_params: QuerySetParams,
                   query: str, year: str, month: str, day: str) -> bool:
    """
    Get the date query
    :param query_set_params: query params to update
    :param query: query key
    :param year: year
    :param month: month
    :param day: day
    :return: True if successfully added
    """
    success = True
    try:
        date = datetime(
            int(year), int(month), int(day), tzinfo=ZoneInfo("UTC")
        )
        query_set_params.add_and_lookup(
            query, FIELD_LOOKUPS[query], date)
    except ValueError:
        # ignore invalid date
        # TODO add errors to QuerySetParams
        # so they can be returned to user
        success = False
    return success


def get_hidden_query(query_set_params: QuerySetParams,
                     hidden: Hidden, user: User) -> bool:
    """
    Get the hidden status query
    :param query_set_params: query params to update
    :param hidden: hidden status
    :param user: current user
    :return: True if successfully added
    """
    return get_yes_no_ignore_query(
        query_set_params, HIDDEN_QUERY, Hidden.YES, Hidden.NO, Hidden.IGNORE,
        hidden, Hidden, HideStatus.objects.filter(**{
            HideStatus.USER_FIELD: user,
            f'{HideStatus.OPINION_FIELD}__isnull': False
        }).values(HideStatus.OPINION_FIELD)
    )


def get_pinned_query(query_set_params: QuerySetParams,
                     pinned: Pinned, user: User) -> bool:
    """
    Get the pinned status query
    :param query_set_params: query params to update
    :param pinned: pinned status
    :param user: current user
    :return: True if successfully added
    """
    return get_yes_no_ignore_query(
        query_set_params, PINNED_QUERY, Pinned.YES, Pinned.NO, Pinned.IGNORE,
        pinned, Pinned, PinStatus.objects.filter(**{
            PinStatus.USER_FIELD: user,
        }).values(PinStatus.OPINION_FIELD)
    )
