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

from categories import (
    STATUS_DRAFT, STATUS_PREVIEW, STATUS_PUBLISHED
)
from categories.models import Category, Status
from opinions.models import Opinion
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

    @staticmethod
    def create_opinion(index: int, user: User, status: Status,
                       categories: list[Category]) -> Opinion:

        kwargs = BaseOpinionTest.OPINION_INFO[index].copy()
        kwargs[Opinion.TITLE_FIELD] = \
            f'{kwargs[Opinion.TITLE_FIELD]} {user.first_name}'
        kwargs[Opinion.USER_FIELD] = user
        kwargs[Opinion.STATUS_FIELD] = status
        kwargs[Opinion.SLUG_FIELD] = Opinion.generate_slug(
            Opinion.OPINION_ATTRIB_SLUG_MAX_LEN,
            kwargs[Opinion.TITLE_FIELD])
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

        for user_idx in range(BaseOpinionTest.num_users()):
            user, _ = BaseOpinionTest.get_user_by_index(user_idx)

            for index in range(len(BaseOpinionTest.OPINION_INFO)):

                mod_num = user_idx + index + 2
                categories = [
                    category for idx, category in enumerate(category_list)
                    if idx % mod_num
                ]

                opinion = BaseOpinionTest.create_opinion(
                    index,
                    user,
                    Status.objects.get(
                        name=BaseOpinionTest.STATUSES[
                            index % len(BaseOpinionTest.STATUSES)]),
                    categories
                )
                cls.opinions.append(opinion)
