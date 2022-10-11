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
from typing import Any
from zoneinfo import ZoneInfo

from django.db.models import Q, QuerySet

from categories.models import Status
from user.models import User
from .constants import (
    STATUS_QUERY, CONTENT_QUERY, CATEGORY_QUERY, AUTHOR_QUERY,
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY, SEARCH_QUERY, OPINION_ID_QUERY, PARENT_ID_QUERY
)
from .models import Opinion, Comment
from .views_utils import (
    QueryStatus,
    QueryArg, NON_REORDER_COMMENT_LIST_QUERY_ARGS
)

# chars used to delimit queries
MARKER_CHARS = ['=', '"', "'"]

NON_DATE_QUERIES = [
    CONTENT_QUERY, AUTHOR_QUERY, STATUS_QUERY
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
    # TODO opinion
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#exact
    STATUS_QUERY: f'{Comment.STATUS_FIELD}__{Status.NAME_FIELD}',
    CONTENT_QUERY: f'{Comment.CONTENT_FIELD}__icontains',
    AUTHOR_QUERY: f'{Comment.USER_FIELD}__{User.USERNAME_FIELD}__icontains',
    OPINION_ID_QUERY: f'{Comment.OPINION_FIELD}__{Opinion.ID_FIELD}',
    PARENT_ID_QUERY: f'{Comment.PARENT_FIELD}',
    # TODO search created date or updated date?
    ON_OR_AFTER_QUERY: f'{Comment.UPDATED_FIELD}__date__gte',
    ON_OR_BEFORE_QUERY: f'{Comment.UPDATED_FIELD}__date__lte',
    AFTER_QUERY: f'{Comment.UPDATED_FIELD}__date__gt',
    BEFORE_QUERY: f'{Comment.UPDATED_FIELD}__date__lt',
    EQUAL_QUERY: f'{Comment.UPDATED_FIELD}__date',
}
# priority order list of query terms
COMMENT_FILTERS_ORDER = [
    # search is a shortcut filter, if search is specified nothing
    # else is checked after
    SEARCH_QUERY,
]
COMMENT_ALWAYS_FILTERS = [
    # always applied items
    STATUS_QUERY,
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
            query: str, value: Any, was_set: bool = False
        ) -> tuple[bool, dict[Any, Any], list[Any]]:
    """
    Get the query lookup for the specified
    :param query: query argument
    :param value: argument value
    :param was_set: value was set (so should be included) flag
    :return: tuple of AND lookups and OR lookups
    """
    and_lookups = {}
    or_lookups = []

    if query in [SEARCH_QUERY, CATEGORY_QUERY] or query in DATE_QUERIES:
        terms, ands, ors = get_comment_search_term(value)
        if terms:
            and_lookups.update(ands)
            or_lookups.extend(ors)
    elif query == STATUS_QUERY:
        if value != QueryStatus.ALL:
            and_lookups[
                FIELD_LOOKUPS[query]] = value.display
        # else do not include status in query
    elif value or was_set:
        and_lookups[
            FIELD_LOOKUPS[query]] = value

    return \
        len(and_lookups) > 0 or len(or_lookups) > 0, and_lookups, or_lookups


def get_comment_search_term(value: str) -> tuple[bool, dict, list]:
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
            if query == STATUS_QUERY:
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
            for q in to_query:
                or_lookups.append(
                    Q(_connector=Q.OR, **{FIELD_LOOKUPS[q]: term
                                          for term in or_q[q]})
                )

    return \
        len(and_lookups) > 0 or len(or_lookups) > 0, and_lookups, or_lookups


def get_comment_queryset(query_params: dict[str, QueryArg]) -> QuerySet:
    """
    Get the queryset to get the list of comments
    :param query_params: request query
    :return: query set
    """
    and_lookups = {}
    for query in NON_REORDER_COMMENT_LIST_QUERY_ARGS:
        if query in query_params:
            param = query_params[query]
            was_set = False
            if isinstance(param, QueryArg):
                was_set = param.was_set
                param = param.value
            _, ands, _ = get_comment_lookup(query, param, was_set=was_set)
            and_lookups.update(ands)

    return Comment.objects.filter(**and_lookups)
