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
from django.test import TestCase

from categories.models import Status
from opinions.constants import (
    STATUS_QUERY, HIDDEN_QUERY, CONTENT_QUERY, AUTHOR_QUERY
)
from utils import DESC_LOOKUP, DATE_NEWEST_LOOKUP
from opinions.models import Comment
from opinions.views.utils import DATE_QUERIES
from opinions.enums import PerPage, CommentSortOrder, QueryStatus, Hidden
from user.models import User
from .base_content_test import ContentTestBase
from .base_opinion_test import (
    SortCtrl, text_in_field, date_check, multi_sort, partial_status_search
)


class BaseCommentTest(ContentTestBase):
    """
    Base class for comment test cases
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    @staticmethod
    def get_expected(
                test_case: TestCase, query: dict, order: CommentSortOrder,
                user: User, per_page: [PerPage, None] = None,
                page_num: int = 0
            ) -> list[Comment]:
        """
        Generate the expected results list
        :param test_case: test case
        :param query: query parameters
        :param order: sort order of results
        :param user: current user
        :param per_page: results per page; default None will return all
        :param page_num: 0-based number of page to get; default 0
        """
        if not isinstance(test_case, BaseCommentTest):
            raise ValueError(f'Not a comment-related test')

        # default status is published if no term in query
        status = QueryStatus.from_arg(query.get(STATUS_QUERY,
                                                QueryStatus.PUBLISH.arg))
        if status is None and STATUS_QUERY in query:
            # try partial match
            status = query.get(STATUS_QUERY)
            status = partial_status_search(status)
            if len(status) == 1:
                status = status[0]

        expected = test_case.published_comments() \
            if status == QueryStatus.PUBLISH else \
            test_case.preview_comments() if status == QueryStatus.PREVIEW \
            else test_case.draft_comments() if status == QueryStatus.DRAFT \
            else test_case.comments

        # default is unhidden if no term in query
        hidden = Hidden.from_arg(query.get(HIDDEN_QUERY, Hidden.NO.arg))
        # if status == QueryStatus.PUBLISH or status == QueryStatus.ALL:
        #     # modify expected to reflect hidden requirement
        #     exclude_list = test_case.user_unhidden_comments(user) \
        #         if hidden == Hidden.YES else \
        #         test_case.user_hidden_comments(user) if hidden == Hidden.NO \
        #         else []
        #     expected = list(filter(
        #         lambda op: op.status.name != STATUS_PUBLISHED or
        #         op not in exclude_list,
        #         expected
        #     ))

        for k, val in query.items():
            if val is None:
                continue
            filter_func = None
            if k in [CONTENT_QUERY]:
                filter_func = text_in_field(Comment.CONTENT_FIELD, val)
            elif k == AUTHOR_QUERY:
                filter_func = text_in_field([
                    Comment.USER_FIELD,
                    User.USERNAME_FIELD
                ], val)
            elif k == STATUS_QUERY:
                if status != QueryStatus.ALL:
                    query_status = partial_status_search(val)
                    test_case.assertEqual(len(query_status), 1,
                                          f'QueryStatus {val} not found')

                    filter_func = text_in_field([
                        Comment.STATUS_FIELD,
                        Status.NAME_FIELD
                    ], query_status[0].display)
                # else all statuses so no need for filtering
            elif k == HIDDEN_QUERY:
                pass
                # if hidden != Hidden.IGNORE:
                #     hidden_status = \
                #         list(filter(lambda h: v in h.arg, Hidden))
                #     test_case.assertEqual(len(hidden_status), 1,
                #                           f'Hidden {v} not found')
                #     hidden_status = hidden_status[0]
                #
                #     # comments hidden by current user
                #     hidden_opinions = [
                #         h.opinion.id for h in HideStatus.objects.all()
                #         if h.user.id == user.id
                #     ]
                #     if hidden_status == Hidden.YES:
                #         def is_hidden(op):
                #             return op.id in hidden_opinions
                #         filter_func = is_hidden
                #     elif hidden_status == Hidden.NO:
                #         def is_not_hidden(op):
                #             return op.id not in hidden_opinions
                #         filter_func = is_not_hidden
                #     else:
                #         raise NotImplementedError(f'{hidden_status}')
                # else hidden status ignored so no need for filtering
            elif k in DATE_QUERIES:
                filter_func = date_check(val, k)

            expected = list(
                filter(
                    filter_func, expected
                ))
            if len(expected) == 0:
                break   # skip unnecessary additional filtering

        return sort_expected(
            expected, order, per_page, page_num=page_num)


def sort_expected(expected: list[Comment], order: CommentSortOrder,
                  per_page: [PerPage, None], page_num: int = 0
                  ) -> list[Comment]:
    """
    Sort the expected results list
    :param expected: expected results
    :param order: sort order of results
    :param per_page: results per page; None will return all
    :param page_num: 0-based number of page to get
    """
    # initial sort is by date, author or status
    current_field = order.to_field()
    expected.sort(
        key=lambda entry:
        getattr(entry, current_field) if order.is_date_order else
        entry.user.username.lower() if order.is_author_order else
        entry.status.name.lower(),
        reverse=order.order.startswith(DESC_LOOKUP)
    )
    sort_ctrl = []
    default_field = CommentSortOrder.DEFAULT.to_field()
    if current_field != default_field:
        # add secondary sort by default sort option
        sort_ctrl.append(
            SortCtrl(
                current_field, default_field,
                reverse=CommentSortOrder.DEFAULT.order.startswith(
                    DESC_LOOKUP))
        )
        current_field = default_field

    # final sort by updated and id
    sort_ctrl.append(
        SortCtrl(   # sort by updated desc, i.e. newest first
            current_field, Comment.UPDATED_FIELD,
            reverse=DATE_NEWEST_LOOKUP == DESC_LOOKUP)
    )
    sort_ctrl.append(
        SortCtrl(   # sort by id asc
            Comment.UPDATED_FIELD, Comment.id_field(), reverse=False)
    )

    expected = multi_sort(expected.copy(), sort_ctrl)

    # contents of requested page
    if per_page is not None:
        start = per_page.arg * page_num
        expected = expected[start:start + per_page.arg]
    return expected
