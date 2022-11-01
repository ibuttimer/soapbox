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
from datetime import datetime, date
from zoneinfo import ZoneInfo

from django.test import TestCase

from categories import STATUS_PUBLISHED
from categories.models import Category, Status
from opinions.constants import (
    STATUS_QUERY, HIDDEN_QUERY, TITLE_QUERY, CONTENT_QUERY, AUTHOR_QUERY,
    CATEGORY_QUERY, ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY,
    BEFORE_QUERY, PUBLISHED_FIELD, DESC_LOOKUP, DATE_NEWEST_LOOKUP
)
from opinions.models import Opinion, HideStatus
from opinions.views.utils import DATE_QUERIES
from opinions.enums import PerPage, OpinionSortOrder, QueryStatus, Hidden
from user.models import User
from .base_content_test import ContentTestBase


DATE_SPACED_FMT = "%d %m %Y"
DATE_SLASHED_FMT = "%d/%m/%Y"
DATE_DASHED_FMT = "%d-%m-%Y"
DATE_DOTTED_FMT = "%d.%m.%Y"


class BaseOpinionTest(ContentTestBase):
    """
    Base class for opinion test cases
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    @staticmethod
    def get_expected(
                test_case: TestCase, query: dict, order: OpinionSortOrder,
                user: User, per_page: [PerPage, None] = None,
                page_num: int = 0
            ) -> list[Opinion]:
        """
        Generate the expected results list
        :param test_case: test case
        :param query: query parameters
        :param order: sort order of results
        :param user: current user
        :param per_page: results per page; default None will return all
        :param page_num: 0-based number of page to get; default 0
        """
        if not isinstance(test_case, BaseOpinionTest):
            raise ValueError('Not an opinion-related test')

        # default status is published if no term in query
        status = QueryStatus.from_arg(query.get(STATUS_QUERY,
                                                QueryStatus.PUBLISH.arg))
        if status is None and STATUS_QUERY in query:
            # try partial match
            status = query.get(STATUS_QUERY)
            status = list(filter(lambda qs: status in qs.arg, QueryStatus))
            if len(status) == 1:
                status = status[0]

        expected = test_case.published_opinions() \
            if status == QueryStatus.PUBLISH else \
            test_case.preview_opinions() if status == QueryStatus.PREVIEW \
            else test_case.draft_opinions() if status == QueryStatus.DRAFT \
            else test_case.opinions

        # default is unhidden if no term in query
        hidden = Hidden.from_arg(query.get(HIDDEN_QUERY, Hidden.NO.arg))
        if status == QueryStatus.PUBLISH or status == QueryStatus.ALL:
            # modify expected to reflect hidden requirement
            exclude_list = test_case.user_unhidden_opinions(user) \
                if hidden == Hidden.YES else \
                test_case.user_hidden_opinions(user) if hidden == Hidden.NO \
                else []
            expected = list(filter(
                lambda op: op.status.name != STATUS_PUBLISHED or
                op not in exclude_list,
                expected
            ))

        for k, v in query.items():
            if v is None:
                continue
            filter_func = None
            if k in [TITLE_QUERY, CONTENT_QUERY]:
                filter_func = text_in_field(
                    Opinion.TITLE_FIELD if k == TITLE_QUERY
                    else Opinion.CONTENT_FIELD, v)
            elif k == AUTHOR_QUERY:
                filter_func = text_in_field([
                    Opinion.USER_FIELD,
                    User.USERNAME_FIELD
                ], v)
            elif k == STATUS_QUERY:
                if status != QueryStatus.ALL:
                    query_status = \
                        list(filter(lambda qs: v in qs.arg, QueryStatus))
                    test_case.assertEqual(len(query_status), 1,
                                          f'QueryStatus {v} not found')

                    filter_func = text_in_field([
                        Opinion.STATUS_FIELD,
                        Status.NAME_FIELD
                    ], query_status[0].display)
                # else all statuses so no need for filtering
            elif k == HIDDEN_QUERY:
                if hidden != Hidden.IGNORE:
                    hidden_status = \
                        list(filter(lambda h: v in h.arg, Hidden))
                    test_case.assertEqual(len(hidden_status), 1,
                                          f'Hidden {v} not found')
                    hidden_status = hidden_status[0]

                    # opinions hidden by current user
                    hidden_opinions = [
                        h.opinion.id for h in HideStatus.objects.all()
                        if h.user.id == user.id
                    ]
                    if hidden_status == Hidden.YES:
                        def is_hidden(op):
                            return op.id in hidden_opinions
                        filter_func = is_hidden
                    elif hidden_status == Hidden.NO:
                        def is_not_hidden(op):
                            return op.id not in hidden_opinions
                        filter_func = is_not_hidden
                    else:
                        raise NotImplementedError(f'{hidden_status}')
                # else hidden status ignored so no need for filtering
            elif k == CATEGORY_QUERY:
                filter_func = category_in_list(v)
            elif k in DATE_QUERIES:
                filter_func = date_check(v, k)

            expected = list(
                filter(
                    filter_func, expected
                ))
            if len(expected) == 0:
                break   # skip unnecessary additional filtering

        return sort_expected(
            expected, order, per_page, page_num=page_num)


SortCtrl = namedtuple(
    'SortCtrl',
    ['chunk_field', 'sort_field', 'reverse'],
    defaults=['', '', False]
)
"""
Sort params tuple
chunk_field: field to use to split the list into sections
sort_field: field to use to sort by within the section
reverse: sort in reverse order flag
"""


def sort_expected(expected: list[Opinion], order: OpinionSortOrder,
                  per_page: [PerPage, None], page_num: int = 0
                  ) -> list[Opinion]:
    """
    Sort the expected results list
    :param expected: expected results
    :param order: sort order of results
    :param per_page: results per page; None will return all
    :param page_num: 0-based number of page to get
    """

    # initial sort is by date, author, title or status
    current_field = order.to_field()
    expected.sort(
        key=lambda entry:
        getattr(entry, current_field) if order.is_date_order else
        entry.user.username.lower() if order.is_author_order else
        entry.status.name.lower() if order.is_status_order else
        entry.title.lower(),
        reverse=order.order.startswith(DESC_LOOKUP)
    )

    sort_ctrl = []
    default_field = OpinionSortOrder.DEFAULT.to_field()
    if current_field != default_field:
        # add secondary sort by default sort option
        sort_ctrl.append(
            SortCtrl(
                current_field, default_field,
                reverse=OpinionSortOrder.DEFAULT.order.startswith(
                    DESC_LOOKUP))
        )
        current_field = default_field

    # final sort by updated and id
    sort_ctrl.append(
        SortCtrl(   # sort by updated desc, i.e. newest first
            current_field, Opinion.UPDATED_FIELD,
            reverse=DATE_NEWEST_LOOKUP == DESC_LOOKUP)
    )
    sort_ctrl.append(
        SortCtrl(   # sort by id asc
            Opinion.UPDATED_FIELD, Opinion.ID_FIELD, reverse=False)
    )

    expected = multi_sort(expected.copy(), sort_ctrl)

    # contents of requested page
    if per_page is not None:
        start = per_page.arg * page_num
        expected = expected[start:start + per_page.arg]
    return expected


def multi_sort(to_sort: list, sort_params: list[SortCtrl]) -> list:
    """
    Sort a list using multiple sort orders; primary sort followed by sorting
    common chunks of list with secondary sort order etc.
    :param to_sort: list to sort
    :param sort_params: list of sort params in descending order of precedence
    :return: sorted list
    """
    result = [] if len(sort_params) > 0 else to_sort

    while len(result) < len(to_sort):
        # sort in chunks of same attrib value
        look_for = getattr(
            to_sort[len(result)], sort_params[0].chunk_field)
        chunk = list(
            filter(
                lambda op: look_for == getattr(op, sort_params[0].chunk_field),
                to_sort)
        )
        chunk.sort(
            key=lambda op: getattr(op, sort_params[0].sort_field),
            reverse=sort_params[0].reverse
        )
        result.extend(
            multi_sort(chunk, sort_params[1:])
        )

    return result


def text_in_field(field: [str, list[str]], text: str):
    """
    Check for `text` in the specified field
    :param field: field(s) to check
    :param text: text to look for
    :return: filter function
    """
    fields = [field] if isinstance(field, str) else field

    def func(instance):
        obj = instance
        for fld in fields[:-1]:
            obj = getattr(obj, fld)
        return text in getattr(obj, fields[-1])

    return func


def category_in_list(name: str):
    """
    Check for category in opinion categories
    :param name: name of category
    :return: filter function
    """
    def func(op):
        return len(list(filter(
            lambda cat:
            text_in_field(Category.NAME_FIELD, name)(cat),
            op.categories.all()
        ))) > 0
    return func


def date_check(date_str: str, test: str, field: str = PUBLISHED_FIELD):
    """
    Check opinion date satisfies condition
    :param date_str: date
    :param test: test for date
    :param field: date field to check
    :return: filter function
    """
    fmt = DATE_SPACED_FMT if ' ' in date_str else \
        DATE_SLASHED_FMT if '/' in date_str else \
        DATE_DASHED_FMT if '-' in date_str else DATE_DOTTED_FMT
    test_date = datetime.strptime(date_str, fmt)
    test_date = test_date.replace(tzinfo=ZoneInfo("UTC"))
    test_date = date(test_date.year, test_date.month, test_date.day)

    def func(content):
        content_date = getattr(content, field)
        op_date = date(
            content_date.year, content_date.month, content_date.day)
        return op_date >= test_date if test == ON_OR_AFTER_QUERY else \
            op_date <= test_date if test == ON_OR_BEFORE_QUERY else \
            op_date > test_date if test == AFTER_QUERY else \
            op_date < test_date if test == BEFORE_QUERY else \
            op_date == test_date    # EQUAL_QUERY

    return func


def middle_word(text: str):
    """
    Get middle word in text
    :param text:
    :return:
    """
    split = text.split()
    return split[int(len(split) / 2)]
