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
from enum import Enum, auto
from typing import Optional, Union, Type

from django.db import models
from django.db.models import QuerySet, Q

from categories import (
    STATUS_WITHDRAWN, STATUS_REJECTED, STATUS_PUBLISHED
)
from categories.models import Status
from user.models import User
from .enums import QueryStatus
from .models import (
    Opinion, PinStatus, Review, Comment, HideStatus, FollowStatus
)
from .query_params import QuerySetParams


def opinion_is_pinned(opinion: Opinion, user: User = None) -> bool:
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


def content_is_hidden(
        content: [Opinion, Comment], user: User = None) -> bool:
    """
    Check if an opinion is pinned
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :return: True if user has pinned opinion
    """
    return get_content_status(content, StatusCheck.HIDDEN, user=user).hidden


def following_content_author(
        content: [Opinion, Comment], user: User = None) -> bool:
    """
    Check if user is following content author
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :return: True if user is following
    """
    query_args = {
        FollowStatus.AUTHOR_FIELD: content.user
    }
    if user:
        query_args[FollowStatus.USER_FIELD] = user
    query = FollowStatus.objects.filter(**query_args)
    return query.exists()


def is_following(
        user: User = None, as_params: bool = False) -> Union[QuerySet, dict]:
    """
    Get list of authors the specified user is following
    :param user: user to check with; default None, i.e. any user
    :param as_params: return dict of params flag: default False
    :return: query set or query param dict
    """
    if user and not user.is_anonymous:
        query_params = {
            FollowStatus.USER_FIELD: user
        }
        query = query_params if as_params else \
            FollowStatus.objects.filter(**query_params)
    else:
        query = FollowStatus.objects.none()

    return query


@dataclass
class ContentStatus:
    """ Review status for Opinion/Comment """

    reported: bool      # was reported
    viewable: bool      # ok to view (with respect to reporting)
    review_wip: bool    # review in progress
    hidden: bool        # was hidden (has precedence over viewable)
    mine: bool          # current user's content (has precedence over hidden)

    @property
    def view_ok(self):
        """ Ok to view """
        return self.mine or (self.viewable and not self.hidden)

    @property
    def review_no_show(self):
        """ Do not show as in review """
        return self.review_wip and not self.mine


ContentStatus.VIEW_OK = ContentStatus(
    reported=False, viewable=True, review_wip=False, hidden=False,
    mine=False
)


def content_status_check(
        content: Union[Opinion, Comment], user: User = None,
        current_user: User = None) -> ContentStatus:
    """
    Check the status of content
    :param content: content to check
    :param user: user to check with; default None, i.e. any user
    :param current_user: user making request; default None
    :return: ContentStatus
    """
    return get_content_status(
        content, StatusCheck.ALL, user=user, current_user=current_user)


class StatusCheck(Enum):
    """ Enum of status checks for content """
    ALL = auto()
    REPORTED = auto()
    VIEWABLE = auto()
    REVIEW_WIP = auto()
    HIDDEN = auto()


def get_content_status(
        content: [Opinion, Comment], *args, user: User = None,
        current_user: User = None) -> ContentStatus:
    """
    Get content status, i.e. reported, ok to view, review wip and hidden.
    If a user is specified, check it with respect to that user, otherwise
    any user.
    :param content: content to check
    :param user: user to check with respect to; default None, i.e. any user
    :param current_user: user making request; default None
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
            ] = [
                stat.display for stat in QueryStatus.review_wip_statuses()
            ]
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
        hidden=hidden,
        mine=content.user.id == current_user.id if current_user else False)


def content_review_status(
    content: [Opinion, Comment], query_args: dict = None
) -> Optional[Status]:
    """
    Get the review status for the specified content
    :param content: content to check
    :param query_args: additional query params: default None
    :return: status
    """
    if query_args is None:
        query_args = {}

    query_args[Review.content_field(content)] = content

    review = Review.objects.filter(**query_args)\
        .order_by(f'-{Review.UPDATED_FIELD}').first()
    return review.status if review else None


def content_is(
        content: [Opinion, Comment], statuses: list[QueryStatus],
        query_args: dict = None) -> Optional[QueryStatus]:
    """
    Get the review status for the specified content
    :param content: content to check
    :param query_args: additional query params: default None
    :param statuses: list of QueryStatus to check
    :return: status if review wip else None
    """
    status = content_review_status(content, query_args=query_args)
    if status:
        if QueryStatus.from_display(status.name) not in statuses:
            status = None

    return status


def content_is_review_wip(
    content: [Opinion, Comment], query_args: dict = None
) -> Optional[QueryStatus]:
    """
    Get the review status for the specified content
    :param content: content to check
    :param query_args: additional query params: default None
    :return: status if review wip else None
    """
    return content_is(content, QueryStatus.review_wip_statuses(),
                      query_args=query_args)


def effective_content_status(content: [Opinion, Comment]) -> str:
    """
    Get the effective status of the specified content
    :param content: content to check
    :return: status
    """
    status = content_review_status(content)
    if status:
        # has review history, so check review status
        status = QueryStatus.from_display(status.name)
        if status in QueryStatus.review_over_statuses():
            status = None

    if status is None:
        # no reviews or review passed so use content status
        status = QueryStatus.from_display(content.status.name)

    return status.display


def followed_author_publications(
    user: User, since: datetime = None, as_params: bool = False
) -> Optional[Union[QuerySet, QuerySetParams]]:
    """
    Get the list of opinions of authors which the specified user is following
    :param user: user to check
    :param since: updates since datetime: default None, i.e. all
    :param as_params: return dict of params flag: default False
    :return: query set or query param dict
    """
    query = None

    followed_ids = FollowStatus.objects.filter(**{
        FollowStatus.USER_FIELD: user
    }).values_list(FollowStatus.AUTHOR_FIELD, flat=True)

    if len(followed_ids) > 0:
        query_set_params = QuerySetParams()
        query_set_params.add_and_lookup(
            Opinion.USER_FIELD, f"{Opinion.USER_FIELD}__in", followed_ids)
        query_set_params.add_and_lookup(
            Opinion.STATUS_FIELD,
            f"{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}", STATUS_PUBLISHED)

        if since:
            query_set_params.add_and_lookup(
                Opinion.PUBLISHED_FIELD,
                f"{Opinion.PUBLISHED_FIELD}__gte", since)

        query = query_set_params if as_params else \
            query_set_params.apply(Opinion.objects)

    return query


def basic_review_query_params(
    user: User, model: Type[models.Model], since: datetime = None
) -> QuerySetParams:
    """
    Get the basic params for a Review status query
    :param user: user to check
    :param model: model to check for
    :param since: updates since datetime: default None, i.e. all
    :return: query set params
    """
    query_set_params = QuerySetParams()
    query_set_params.add_and_lookup(
        model.USER_FIELD,
        f"{Review.content_field(model)}__{model.USER_FIELD}", user)
    if since:
        query_set_params.add_and_lookup(
            Review.UPDATED_FIELD, f"{Review.UPDATED_FIELD}__gte", since)

    return query_set_params


def own_content_status_changes(
    user: User, model: Type[models.Model], since: datetime = None,
    as_params: bool = False
) -> Optional[Union[QuerySet, QuerySetParams]]:
    """
    Get the list of opinions for which the Review status has changed
    :param user: user to check
    :param model: model to check for
    :param since: updates since datetime: default None, i.e. all
    :param as_params: return dict of params flag: default False
    :return: query set or query param dict
    """
    query_set_params = basic_review_query_params(user, model, since=since)

    return query_set_params if as_params else \
        query_set_params.apply(Review.objects)


def in_review_content(
    user: User, model: Type[models.Model], since: datetime = None,
    as_params: bool = False
) -> Optional[Union[QuerySet, dict]]:
    """
    Get the list of opinions which are in review
    :param user: user to check
    :param model: model to check for
    :param since: updates since datetime: default None, i.e. all
    :param as_params: return dict of params flag: default False
    :return: query set or query param dict
    """
    query_set_params = basic_review_query_params(user, model, since=since)

    query_set_params.add_or_lookup(
        Review.STATUS_FIELD,
        Q(_connector=Q.OR, *[
            Q(**{f'{Review.STATUS_FIELD}__{Status.NAME_FIELD}': stat.display})
            for stat in QueryStatus.review_wip_statuses()
        ])
    )

    content_field = Review.content_field(model)
    in_review = query_set_params.apply(
        Review.objects).values_list(content_field, flat=True)

    query_set_params.clear()
    if in_review:
        query_set_params.add_and_lookup(
            content_field, f'{Review.id_field()}__in', in_review
        )
    else:
        query_set_params.is_none = True

    return query_set_params if as_params else \
        query_set_params.apply(Review.objects)
