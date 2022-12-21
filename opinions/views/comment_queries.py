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
from typing import Any
from zoneinfo import ZoneInfo

from django.db.models import Q, QuerySet

from categories.models import Status
from opinions.views.opinion_queries import NON_LOOKUP_ARGS
from user.models import User
from opinions.constants import (
    STATUS_QUERY, CONTENT_QUERY, CATEGORY_QUERY, AUTHOR_QUERY,
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY, SEARCH_QUERY, OPINION_ID_QUERY, PARENT_ID_QUERY, HIDDEN_QUERY,
    ID_QUERY
)
from opinions.models import Opinion, Comment
from opinions.query_params import QuerySetParams, choice_arg_query
from opinions.search import (
    regex_matchers, TERM_GROUP, regex_date_matchers, DATE_QUERY_GROUP,
    DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
    DATE_QUERY_DAY_GROUP, MARKER_CHARS
)
from opinions.views.utils import (
    NON_REORDER_COMMENT_LIST_QUERY_ARGS, DATE_QUERIES,
    COMMENT_APPLIED_DEFAULTS_QUERY_ARGS
)
from opinions.enums import QueryArg, QueryStatus


NON_DATE_QUERIES = [
    CONTENT_QUERY, AUTHOR_QUERY, STATUS_QUERY
]
REGEX_MATCHERS = regex_matchers(NON_DATE_QUERIES)
REGEX_MATCHERS.update(regex_date_matchers())

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    # TODO opinion
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#exact
    ID_QUERY: f'{Comment.id_field()}',
    STATUS_QUERY: f'{Comment.STATUS_FIELD}__{Status.NAME_FIELD}',
    CONTENT_QUERY: f'{Comment.CONTENT_FIELD}__icontains',
    AUTHOR_QUERY: f'{Comment.USER_FIELD}__{User.USERNAME_FIELD}__icontains',
    OPINION_ID_QUERY: f'{Comment.OPINION_FIELD}__{Opinion.id_field()}',
    PARENT_ID_QUERY: f'{Comment.PARENT_FIELD}',
    ON_OR_AFTER_QUERY: f'{Comment.SEARCH_DATE_FIELD}__date__gte',
    ON_OR_BEFORE_QUERY: f'{Comment.SEARCH_DATE_FIELD}__date__lte',
    AFTER_QUERY: f'{Comment.SEARCH_DATE_FIELD}__date__gt',
    BEFORE_QUERY: f'{Comment.SEARCH_DATE_FIELD}__date__lt',
    EQUAL_QUERY: f'{Comment.SEARCH_DATE_FIELD}__date',
}
# priority order list of query terms
COMMENT_FILTERS_ORDER = [
    # search is a shortcut filter, if search is specified nothing
    # else is checked after
    SEARCH_QUERY,
]
COMMENT_ALWAYS_FILTERS = [
    # always applied items
    option.query for option in COMMENT_APPLIED_DEFAULTS_QUERY_ARGS
]
COMMENT_FILTERS_ORDER.extend(
    [q for q in FIELD_LOOKUPS.keys() if q not in COMMENT_FILTERS_ORDER]
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


def get_comment_lookup(
            query: str, value: Any, user: User, was_set: bool = False,
            query_set_params: QuerySetParams = None
        ) -> QuerySetParams:
    """
    Get the query lookup for the specified
    :param query: query argument
    :param value: argument value
    :param user: current user
    :param was_set: value was set (so should be included) flag
    :param query_set_params: query set params
    :return: query set params
    """
    if query_set_params is None:
        query_set_params = QuerySetParams()

    if query in [SEARCH_QUERY, CATEGORY_QUERY] or query in DATE_QUERIES:
        query_set_params = get_comment_search_term(
            value, user, query_set_params=query_set_params)
    elif query == STATUS_QUERY:
        if value == QueryStatus.ALL:
            query_set_params.add_all_inclusive(query)
        else:
            query_set_params.add_and_lookup(
                query, FIELD_LOOKUPS[query], value.display)
        # else do not include status in query
    elif query == HIDDEN_QUERY:
        # get_hidden_query(query_set_params, value, user)
        pass
    elif query not in NON_LOOKUP_ARGS and (value or was_set):
        query_set_params.add_and_lookup(query, FIELD_LOOKUPS[query], value)

    return query_set_params


def get_comment_search_term(
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

    for regex, query, group in SEARCH_REGEX:
        match = regex.match(value)
        if match:
            if query == STATUS_QUERY:
                # need inner queryset to get list of statuses with names
                # like the search term and then look for opinions with those
                # statuses
                choice_arg_query(
                    query_set_params, match.group(group).lower(),
                    QueryStatus, QueryStatus.ALL,
                    Status, Status.NAME_FIELD, query, FIELD_LOOKUPS[query]
                )
            elif query == HIDDEN_QUERY:
                # need to filter/exclude by list of comments that the user has
                # hidden
                pass
                # hidden = Hidden.from_arg(match.group(group).lower())
                # get_hidden_query(query_set_params, hidden, user)
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
            # no delimiting chars, so search content for
            # any of the search terms
            to_query = [CONTENT_QUERY]
            or_q = {}
            for term in value.split():
                if len(or_q) == 0:
                    or_q = {q: [term] for q in to_query}
                else:
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


def get_comment_queryset(
        query_params: dict[str, QueryArg], user: User) -> QuerySet:
    """
    Get the queryset to get the list of comments
    :param query_params: request query
    :param user: current user
    :return: query set
    """
    query_set_params = QuerySetParams()
    for query in NON_REORDER_COMMENT_LIST_QUERY_ARGS:
        if query in query_params:
            param = query_params[query]
            was_set = False
            if isinstance(param, QueryArg):
                was_set = param.was_set
                param = param.value
            get_comment_lookup(query, param, user, was_set=was_set,
                               query_set_params=query_set_params)

    return query_set_params.apply(Comment.objects)
