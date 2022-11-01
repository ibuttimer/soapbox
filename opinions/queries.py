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
from enum import Enum, auto

from categories import (
    STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW, STATUS_WITHDRAWN,
    STATUS_REJECTED
)
from categories.models import Status
from user.models import User
from .data_structures import ContentStatus
from .models import Opinion, PinStatus, Review, Comment, HideStatus


def opinion_is_pinned(opinion: Opinion, user: User = None):
    """
    Check if an opinion is pinned
    :param opinion: opinion to check
    :param user: user to check with; default None, i.e. any user
    :return: True if user has pinned opinion
    """
    query_args = {
        PinStatus.OPINION_FIELD: opinion
    }
    if user:
        query_args[PinStatus.USER_FIELD] = user
    query = PinStatus.objects.filter(**query_args)
    return query.exists()


def content_status_check(
        content: [Opinion, Comment], user: User = None) -> ContentStatus:
    """
    Check the status of content
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :return: ContentStatus
    """
    return get_content_status(content, StatusCheck.ALL, user=user)


class StatusCheck(Enum):
    """ Enum of status checks for content """
    ALL = auto()
    REPORTED = auto()
    VIEWABLE = auto()
    REVIEW_WIP = auto()
    HIDDEN = auto()


def get_content_status(content: [Opinion, Comment], *args,
                       user: User = None) -> ContentStatus:
    """
    Get content status, i.e. reported, ok to view, review wip and hidden.
    If a user is specified, check it with respect to that user, otherwise
    any user.
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :param args: list of StatusCheck to check
    :return: ContentStatus
    """
    checked = {
        key: False for key in StatusCheck
    }
    reported = StatusCheck.ALL in args or StatusCheck.REPORTED in args
    review_wip = StatusCheck.ALL in args or StatusCheck.REVIEW_WIP in args
    viewable = StatusCheck.ALL in args or StatusCheck.VIEWABLE in args
    hidden = StatusCheck.ALL in args or StatusCheck.HIDDEN in args

    if reported or review_wip or viewable:
        # check if reported
        query_args = {
            Review.content_field(content): content
        }
        if user:
            query_args[Review.REQUESTED_FIELD] = user
        query = Review.objects.filter(**query_args)
        reported = query.exists()
        checked[StatusCheck.REPORTED] = True

        if review_wip:
            # review process under way if:
            # - status is review pending or under review
            chk_args = query_args.copy()
            chk_args[
                f'{Review.STATUS_FIELD}__{Status.NAME_FIELD}__in'
            ] = [STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW]
            query = Review.objects.filter(**chk_args)
            review_wip = query.exists()
            checked[StatusCheck.REVIEW_WIP] = True

        if viewable:
            # ok to view if:
            # - not reported
            # - status is review withdrawn or review rejected
            viewable = not reported
            if not viewable:
                chk_args = query_args.copy()
                chk_args[
                    f'{Review.STATUS_FIELD}__{Status.NAME_FIELD}__in'
                ] = [STATUS_WITHDRAWN, STATUS_REJECTED]
                query = Review.objects.filter(**chk_args)
                viewable = query.exists()
            checked[StatusCheck.VIEWABLE] = True

    if hidden:
        # check if hidden
        query_args = {
            HideStatus.content_field(content): content
        }
        if user:
            query_args[HideStatus.USER_FIELD] = user
        query = HideStatus.objects.filter(**query_args)
        hidden = query.exists()

    return ContentStatus(
        reported=reported, viewable=viewable, review_wip=review_wip,
        hidden=hidden)
