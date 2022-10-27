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
from categories import STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW, \
    STATUS_WITHDRAWN, STATUS_REJECTED
from categories.models import Status
from user.models import User
from .data_structures import ReviewStatus
from .models import Opinion, PinStatus, Review, Comment


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


def review_status_check(
        content: [Opinion, Comment], user: User = None) -> ReviewStatus:
    """
    Check the review status of an opinion
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :return: ReviewStatus
    """
    return content_is_reported(
        content, user=user, view_ok=True, review_wip=True)


def content_is_reported(content: [Opinion, Comment], user: User = None,
                        view_ok: bool = False,
                        review_wip: bool = False) -> ReviewStatus:
    """
    Check if an opinion has been reported by any user, or reported by the
    specified user
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :param view_ok: check if ok for viewing; default False no check
    :param review_wip: check if review in progress; default False no check
    :return: ReviewStatus
    """
    query_args = {
        Review.OPINION_FIELD if isinstance(content, Opinion)
        else Review.COMMENT_FIELD: content
    }
    if user:
        query_args[Review.REQUESTED_FIELD] = user
    query = Review.objects.filter(**query_args)
    reported = query.exists()

    if review_wip:
        # review process under way if:
        # - status is review pending or under review
        wip_args = query_args.copy()
        wip_args[
            f'{Review.STATUS_FIELD}__{Status.NAME_FIELD}__in'
        ] = [STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW]
        query = Review.objects.filter(**wip_args)
        review_wip = query.exists()

    if view_ok:
        # ok to view if:
        # - not reported
        # - status is review withdrawn or review rejected
        view_ok = not reported
        if not view_ok:
            wip_args = query_args.copy()
            wip_args[
                f'{Review.STATUS_FIELD}__{Status.NAME_FIELD}__in'
            ] = [STATUS_WITHDRAWN, STATUS_REJECTED]
            query = Review.objects.filter(**wip_args)
            view_ok = query.exists()

    return ReviewStatus(
        reported=reported, view_ok=view_ok, review_wip=review_wip)
