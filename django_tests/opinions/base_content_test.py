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
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from categories import (
    STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED, STATUS_PENDING_REVIEW
)
from categories.models import Category, Status
from opinions.constants import (
    OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS
)
from opinions.models import Opinion, Comment, HideStatus, Review
from opinions.views.utils import generate_excerpt
from opinions.enums import PerPage
from user.models import User
from ..user.base_user_test import BaseUserTest


class ContentTestBase(BaseUserTest):
    """
    Base class for content test cases
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    OPINION_INFO = [{
            Opinion.TITLE_FIELD: opinion[0],
            Opinion.CONTENT_FIELD: opinion[1],
        } for opinion in [
            ("Title 1 informative", "Very informative opinion"),
            ("Title 2 controversial", "Very controversial opinion"),
            ("Title 3 ground-breaking", "Ground-breaking opinion"),
        ]
    ]
    STATUSES = [STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED]

    opinions: list[Opinion]
    hidden_opinions: list[Opinion]
    reported_opinions: list[Opinion]
    comments: list[Comment]
    reported_comments: list[Comment]

    @staticmethod
    def create_opinion(
            index: int, user: User, status: Status,
            categories: list[Category], days: int,
            hidden: bool = False, reported: bool = False) -> Opinion:
        other_user = None
        title_addendum = ''
        if hidden or reported:
            other_user = ContentTestBase.get_other_user(user)
        if hidden:
            title_addendum = f'{title_addendum} hidden[{other_user.username}]'
        if reported:
            title_addendum = f'{title_addendum} report[{other_user.username}]'

        kwargs = ContentTestBase.OPINION_INFO[
            index % len(ContentTestBase.OPINION_INFO)].copy()
        kwargs[Opinion.TITLE_FIELD] = \
            f'{kwargs[Opinion.TITLE_FIELD]} {user.first_name} {index}' \
            f'{title_addendum}'
        kwargs[Opinion.USER_FIELD] = user
        kwargs[Opinion.STATUS_FIELD] = status
        if status.name == STATUS_PUBLISHED:
            kwargs[Opinion.PUBLISHED_FIELD] = \
                datetime(2022, 1, 1, hour=12, tzinfo=ZoneInfo("UTC")) + \
                timedelta(days=days)
        kwargs[Opinion.EXCERPT_FIELD] = generate_excerpt(
            kwargs[Opinion.CONTENT_FIELD])
        opinion = Opinion(**kwargs)
        opinion.set_slug(kwargs[Opinion.TITLE_FIELD])
        opinion.save()
        opinion.categories.set(categories)
        opinion.save()

        if hidden:
            kwargs = {
                HideStatus.OPINION_FIELD: opinion,
                HideStatus.USER_FIELD: other_user,
            }
            HideStatus.objects.create(**kwargs)

        if reported:
            ContentTestBase.report_content(opinion, other_user)

        return opinion

    @staticmethod
    def report_content(content: [Opinion, Comment], reporter: User):
        kwargs = {
            Review.content_field(content): content,
            Review.REQUESTED_FIELD: reporter,
            Review.REASON_FIELD: f'{reporter} is offended',
            Review.STATUS_FIELD:
                Status.objects.get(name=STATUS_PENDING_REVIEW),
        }
        Review.objects.create(**kwargs)

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(ContentTestBase, ContentTestBase).setUpTestData()
        # create opinions
        category_list = list(Category.objects.all())

        cls.opinions = []
        cls.hidden_opinions = []
        cls.reported_opinions = []
        cls.comments = []
        cls.reported_comments = []
        num_templates = len(ContentTestBase.OPINION_INFO)

        def get_categories(u_idx, idx):
            m_num = (u_idx + idx + 2) % len(category_list)
            if m_num == 0:
                m_num = 2
            return [
                category for idx, category in enumerate(category_list)
                if idx % m_num == 0
            ]

        days = 0

        # add a draft/preview/published opinion for each user
        for user_idx in range(ContentTestBase.num_users()):
            user, _ = ContentTestBase.get_user_by_index(user_idx)

            for index in range(num_templates):
                opinion = ContentTestBase.create_opinion(
                    (user_idx * num_templates) + index,
                    user,
                    Status.objects.get(
                        name=ContentTestBase.STATUSES[
                            index % len(ContentTestBase.STATUSES)]),
                    get_categories(user_idx, index),
                    days=days
                )
                cls.opinions.append(opinion)
                days += 1

        # add hidden/reported opinions for each user
        published = Status.objects.get(name=STATUS_PUBLISHED)
        for user_idx in range(ContentTestBase.num_users()):
            user, _ = ContentTestBase.get_user_by_index(user_idx)

            for index in range(num_templates):
                for action in range(2):
                    opinion = ContentTestBase.create_opinion(
                        (user_idx * num_templates) + index,
                        user, published,
                        get_categories(user_idx, index),
                        days=days,
                        hidden=True if action else False,
                        reported=False if action else True
                    )
                    cls.opinions.append(opinion)
                    days += 1

                    if action:
                        cls.hidden_opinions.append(opinion)
                    else:
                        cls.reported_opinions.append(opinion)

        # add enough published opinions to get pagination ellipsis
        num_pages = ((OPINION_PAGINATION_ON_ENDS + 1) * 2) + \
                    (OPINION_PAGINATION_ON_EACH_SIDE * 2) + 1
        start = num_templates * ContentTestBase.num_users()
        for index in range(
                start,
                start + (num_pages * PerPage.FIFTEEN.arg)):
            opinion = ContentTestBase.create_opinion(
                index,
                user,
                published,
                get_categories(user_idx, index),
                days=days
            )
            cls.opinions.append(opinion)
            days += 1

        # add comments (normal/reported) on each published opinion
        for index, opinion in enumerate(cls.opinions):
            if opinion.status == published:
                user = cls.get_other_user(opinion.user)

                for cmt_idx in range(2):
                    if index % 2 == 1 and cmt_idx == 1:
                        # only report comments on odd numbered opinions
                        continue

                    reported = f' reported[{user}]' if cmt_idx == 1 else ''

                    comment = Comment.objects.create(**{
                        Comment.CONTENT_FIELD:
                            f"Comment {cmt_idx} from {user.username} "
                            f"on '{opinion}'{reported}",
                        Comment.OPINION_FIELD: opinion,
                        Comment.USER_FIELD: user,
                        Comment.STATUS_FIELD: published,
                        Comment.PUBLISHED_FIELD: datetime(
                            2022, 1, 1, hour=12,
                            tzinfo=ZoneInfo("UTC")) + timedelta(days=days)
                    })
                    comment.set_slug(comment.content)
                    comment.save()

                    cls.comments.append(comment)
                    days += 1

                    if cmt_idx == 1:
                        # report comment
                        ContentTestBase.report_content(comment, user)
                        cls.reported_comments.append(comment)

    @classmethod
    def all_opinions_of_status(cls, name: str) -> list[Opinion]:
        """
        All opinions with the specified status name
        :param name: status name
        :return: list of opinions
        """
        return list(
            filter(
                lambda op: op.published.year > 1 and
                op.status.name == name,
                cls.opinions
            ))

    @classmethod
    def draft_opinions(cls) -> list[Opinion]:
        """ All draft opinions """
        return cls.all_opinions_of_status(STATUS_DRAFT)

    @classmethod
    def preview_opinions(cls) -> list[Opinion]:
        """ All preview opinions """
        return cls.all_opinions_of_status(STATUS_PREVIEW)

    @classmethod
    def published_opinions(cls) -> list[Opinion]:
        """ All published opinions (both hidden and unhidden) """
        return cls.all_opinions_of_status(STATUS_PUBLISHED)

    @classmethod
    def hidden_status_opinions(
            cls, hidden: bool, user: User = None) -> list[Opinion]:
        """
        Get list of opinions of specified hidden status
        :param hidden: hidden status to match
        :param user: get list with respect to user; default None
        :return: list of opinions
        """
        def id_check(usr):
            return usr.id == user.id if user else True

        hidden_opinions = [
            h.opinion.id for h in HideStatus.objects.all() if id_check(h.user)
        ]

        def list_check(op_id):
            return op_id in hidden_opinions \
                if hidden else op_id not in hidden_opinions

        # only published opinions may be hidden
        return [
            op for op in cls.published_opinions() if list_check(op.id)
        ]

    @classmethod
    def user_hidden_opinions(cls, user: User) -> list[Opinion]:
        """
        Get list of hidden opinions for specified user
        :param user: get list with respect to user
        :return: list of opinions
        """
        return cls.hidden_status_opinions(True, user=user)

    @classmethod
    def user_unhidden_opinions(cls, user: User) -> list[Opinion]:
        """
        Get list of unhidden opinions for specified user
        :param user: get list with respect to user
        :return: list of opinions
        """
        return cls.hidden_status_opinions(False, user=user)

    @classmethod
    def all_comments_of_status(cls, name: str) -> list[Comment]:
        """
        All opinions with the specified status name
        :param name: status name
        :return: list of opinions
        """
        return list(
            filter(
                lambda op: op.status.name == name,
                cls.comments
            ))

    @classmethod
    def draft_comments(cls) -> list[Comment]:
        """ All draft opinions """
        return cls.all_comments_of_status(STATUS_DRAFT)

    @classmethod
    def preview_comments(cls) -> list[Comment]:
        """ All preview opinions """
        return cls.all_comments_of_status(STATUS_PREVIEW)

    @classmethod
    def published_comments(cls) -> list[Comment]:
        """ All published opinions """
        return cls.all_comments_of_status(STATUS_PUBLISHED)
