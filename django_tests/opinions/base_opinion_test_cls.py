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
    STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED
)
from categories.models import Category, Status
from opinions.constants import (
    OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS
)
from opinions.models import Opinion
from opinions.views_utils import generate_excerpt, OpinionPerPage
from user.models import User
from ..user.base_user_test_cls import BaseUserTest


class BaseOpinionTest(BaseUserTest):
    """
    Test opinion page view
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

    @staticmethod
    def create_opinion(index: int, user: User, status: Status,
                       categories: list[Category]) -> Opinion:

        kwargs = BaseOpinionTest.OPINION_INFO[
            index % len(BaseOpinionTest.OPINION_INFO)].copy()
        kwargs[Opinion.TITLE_FIELD] = \
            f'{kwargs[Opinion.TITLE_FIELD]} {user.first_name} {index}'
        kwargs[Opinion.USER_FIELD] = user
        kwargs[Opinion.STATUS_FIELD] = status
        if status.name == STATUS_PUBLISHED:
            kwargs[Opinion.PUBLISHED_FIELD] = \
                datetime(2022, 1, 1, hour=12, tzinfo=ZoneInfo("UTC")) + \
                timedelta(days=index)
        kwargs[Opinion.SLUG_FIELD] = Opinion.generate_slug(
            Opinion.OPINION_ATTRIB_SLUG_MAX_LEN,
            kwargs[Opinion.TITLE_FIELD])
        kwargs[Opinion.EXCERPT_FIELD] = generate_excerpt(
            kwargs[Opinion.CONTENT_FIELD])
        opinion = Opinion(**kwargs)
        opinion.save()
        opinion.categories.set(categories)
        opinion.save()
        return opinion

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(BaseOpinionTest, BaseOpinionTest).setUpTestData()
        # create opinions
        category_list = list(Category.objects.all())

        cls.opinions = []
        num_templates = len(BaseOpinionTest.OPINION_INFO)

        def get_categories(u_idx, idx):
            m_num = (u_idx + idx + 2) % len(category_list)
            if m_num == 0:
                m_num = 2
            return [
                category for idx, category in enumerate(category_list)
                if idx % m_num == 0
            ]

        # add a draft/preview/published opinion for each user
        user_idx = 0
        for user_idx in range(BaseOpinionTest.num_users()):
            user, _ = BaseOpinionTest.get_user_by_index(user_idx)

            for index in range(num_templates):
                opinion = BaseOpinionTest.create_opinion(
                    (user_idx * num_templates) + index,
                    user,
                    Status.objects.get(
                        name=BaseOpinionTest.STATUSES[
                            index % len(BaseOpinionTest.STATUSES)]),
                    get_categories(user_idx, index)
                )
                cls.opinions.append(opinion)

        # add enough published opinions to get pagination ellipsis
        published = Status.objects.get(name=STATUS_PUBLISHED)
        num_pages = ((OPINION_PAGINATION_ON_ENDS + 1) * 2) + \
                    (OPINION_PAGINATION_ON_EACH_SIDE * 2) + 1
        start = num_templates * BaseOpinionTest.num_users()
        for index in range(
                start,
                start + (num_pages * OpinionPerPage.FIFTEEN.arg)):
            opinion = BaseOpinionTest.create_opinion(
                index,
                user,
                published,
                get_categories(user_idx, index)
            )
            cls.opinions.append(opinion)

    @classmethod
    def published(cls) -> list[Opinion]:
        """ All published opinions """
        return list(
            filter(
                lambda op: op.published.year > 1 and
                op.status.name == STATUS_PUBLISHED,
                cls.opinions
            ))

    @classmethod
    def all_of_status(cls, name: str) -> list[Opinion]:
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
    def draft(cls) -> list[Opinion]:
        """ All draft opinions """
        return cls.all_of_status(STATUS_DRAFT)

    @classmethod
    def preview(cls) -> list[Opinion]:
        """ All preview opinions """
        return cls.all_of_status(STATUS_PREVIEW)

    @classmethod
    def published(cls) -> list[Opinion]:
        """ All published opinions """
        return cls.all_of_status(STATUS_PUBLISHED)
