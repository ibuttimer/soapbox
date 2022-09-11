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
from http import HTTPStatus

from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.urls import reverse

from categories import STATUS_DRAFT, STATUS_PUBLISHED, CATEGORY_UNASSIGNED
from opinions.constants import OPINION_NEW_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME
from soapbox import OPINIONS_APP_NAME
from opinions import OPINION_ID_ROUTE_NAME
from user.models import User
from categories.models import Category, Status
from opinions.models import Opinion
from ..soup_mixin import SoupMixin
from ..category_mixin import CategoryMixin
from ..user.base_user_test_cls import BaseUserTest


OWN_OPINION_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_form.html'
OTHER_OPINION_TEMPLATE = f'{OPINIONS_APP_NAME}/opinion_view.html'


class TestOpinionView(SoupMixin, CategoryMixin, BaseUserTest):
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
        ]
    ]

    @staticmethod
    def create_opinion(index: int, user: User, status: Status,
                       categories: list[Category]) -> Opinion:

        kwargs = TestOpinionView.OPINION_INFO[index].copy()
        kwargs[Opinion.USER_FIELD] = user
        kwargs[Opinion.STATUS_FIELD] = status
        kwargs[Opinion.SLUG_FIELD] = Opinion.generate_slug(
            Opinion.OPINION_ATTRIB_SLUG_MAX_LEN,
            kwargs[Opinion.TITLE_FIELD])
        opinion = Opinion(**kwargs)
        opinion.save()
        opinion.categories.set(categories)
        return opinion

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionView, TestOpinionView).setUpTestData()
        # create opinions
        category_list = list(Category.objects.all())

        cls.opinions = []

        for index in range(len(TestOpinionView.OPINION_INFO)):

            mod_num = index + 2
            categories = [
                category for idx, category in enumerate(category_list)
                if idx % mod_num
            ]

            user, _ = TestOpinionView.get_user_by_index(index)

            cls.opinions.append(
                TestOpinionView.create_opinion(
                    index,
                    user,
                    Status.objects.get(
                        name=STATUS_DRAFT if index % 2 else STATUS_PUBLISHED),
                    categories
                )
            )

    def login_user_by_key(self, name: str | None = None) -> User:
        """
        Login user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_key(self, name)

    def login_user_by_id(self, pk: int) -> User:
        """
        Login user
        :param pk: id of user to login
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_id(self, pk)

    def get_opinion_by_id(self, pk: int) -> HttpResponse:
        """
        Get the opinion page
        :param pk: id of opinion
        """
        return self.client.get(
            reverse(OPINION_ID_ROUTE_NAME, args=[pk]))

    def get_opinion_by_slug(self, slug: str) -> HttpResponse:
        """
        Get the opinion page
        :param slug: slug of opinion
        """
        return self.client.get(
            reverse(OPINION_SLUG_ROUTE_NAME, args=[slug]))

    def test_not_logged_in_access_by_id(self):
        """ Test must be logged in to access opinion by id """
        response = self.get_opinion_by_id(TestOpinionView.opinions[0].id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_logged_in_access_by_slug(self):
        """ Test must be logged in to access opinion by slug """
        response = self.get_opinion_by_slug(TestOpinionView.opinions[0].slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_own_opinion_by_id(self):
        """ Test page content for opinion by id of logged-in user """
        opinion = TestOpinionView.opinions[0]
        user = self.login_user_by_id(opinion.user.id)
        response = self.get_opinion_by_id(opinion.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OWN_OPINION_TEMPLATE)
        self.verify_opinion_content(opinion, response)

    def test_get_own_opinion_by_slug(self):
        """ Test page content for opinion by slug of logged-in user """
        opinion = TestOpinionView.opinions[0]
        user = self.login_user_by_id(opinion.user.id)
        response = self.get_opinion_by_slug(opinion.slug)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OWN_OPINION_TEMPLATE)
        self.verify_opinion_content(opinion, response)

    def test_get_other_opinion_by_id(self):
        """ Test page content for opinion by id of not logged-in user """
        _, key = TestOpinionView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        opinions = list(
            filter(lambda op: op.user.id != logged_in_user.id,
                   TestOpinionView.opinions)
        )
        self.assertGreaterEqual(len(opinions), 1)
        opinion = opinions[0]

        self.assertNotEqual(logged_in_user, opinion.user)
        response = self.get_opinion_by_id(opinion.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OTHER_OPINION_TEMPLATE)
        self.verify_opinion_content(opinion, response, is_readonly=True)

    def test_get_other_opinion_by_slug(self):
        """ Test page content for opinion by slug of not logged-in user """
        _, key = TestOpinionView.get_user_by_index(0)
        logged_in_user = self.login_user_by_key(key)

        opinions = list(
            filter(lambda op: op.user.id != logged_in_user.id,
                   TestOpinionView.opinions)
        )
        self.assertGreaterEqual(len(opinions), 1)
        opinion = opinions[0]

        self.assertNotEqual(logged_in_user, opinion.user)
        response = self.get_opinion_by_slug(opinion.slug)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OTHER_OPINION_TEMPLATE)
        self.verify_opinion_content(opinion, response, is_readonly=True)

    def verify_opinion_content(
                self, opinion: Opinion, response: HttpResponse,
                is_readonly: bool = False
            ):
        """
        Verify opinion page content for user
        :param opinion: expected opinion
        :param response: opinion response
        :param is_readonly: is readonly flag; default False
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check tag for title
        inputs = soup.find_all(id='id_title')
        self.assertEqual(len(inputs), 1)
        title = inputs[0].text if is_readonly else inputs[0].get('value')
        self.assertTrue(title, opinion.title)

        if is_readonly:
            # check for readonly_content div, can't check content as its
            # replaced by javascript
            self.find_tag(self, soup.find_all(id='readonly_content'),
                          lambda tag: True)
        else:
            # check textarea tags for content
            self.find_tag(self, soup.find_all('textarea'),
                          lambda tag: opinion.content in tag.text)

        # check categories
        if is_readonly:
            TestOpinionView.check_categories(
                self, soup,
                lambda tag: tag.name == 'span'
                and TestOpinionView.in_tag_attr(tag, 'class', 'badge'),
                lambda category, tag: category.name == tag.text,
                opinion.categories.all())
        else:
            TestOpinionView.check_category_options(
                self, soup, opinion.categories.all())

        # check fieldset is disabled in read only mode
        if is_readonly:
            pass    # no fieldset in view mode
        else:
            self.check_tag(self, soup.find_all('fieldset'), is_readonly,
                           lambda tag: tag.has_attr('disabled'))

        # check status only displayed if not read only,
        # i.e. current user's opinion
        found = False
        for span in soup.find_all('span'):
            if TestOpinionView.in_tag_attr(span, 'class', 'badge'):
                found = opinion.status.name == span.text
                if found:
                    break
        if is_readonly:
            self.assertFalse(found)
        else:
            self.assertTrue(found)

        # check submit button only displayed in not read only mode
        tags = soup.find_all(
            lambda tag: tag.name == 'button'
            and TestOpinionView.equal_tag_attr(tag, 'type', 'submit')
        )
        if is_readonly:
            self.assertEqual(len(tags), 0)
        else:
            self.assertEqual(len(tags), 3)


class TestOpinionCreate(SoupMixin, BaseUserTest):
    """
    Test opinion create page
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionCreate, TestOpinionCreate).setUpTestData()

    def login_user_by_key(self, name: str | None = None) -> User:
        """
        Login user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_key(self, name)

    def login_user_by_id(self, pk: int) -> User:
        """
        Login user
        :param pk: id of user to login
        :returns logged-in user
        """
        return BaseUserTest.login_user_by_id(self, pk)

    def get_opinion(self) -> HttpResponse:
        """
        Get the opinion create page
        """
        return self.client.get(
            reverse(OPINION_NEW_ROUTE_NAME))

    def test_not_logged_in_access_opinion(self):
        """ Test must be logged in to access opinion """
        response = self.get_opinion()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_opinion(self):
        """ Test opinion page uses correct template """
        _, key = TestOpinionCreate.get_user_by_index(0)
        user = self.login_user_by_key(key)
        response = self.get_opinion()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, OWN_OPINION_TEMPLATE)

    def test_get_own_opinion_content(self):
        """ Test page content for opinion of logged-in user"""
        _, key = TestOpinionCreate.get_user_by_index(0)
        user = self.login_user_by_key(key)
        response = self.get_opinion()
        self.verify_opinion_content(response)

    def verify_opinion_content(
            self, response: HttpResponse,
            is_readonly: bool = False
    ):
        """
        Verify opinion page content for user
        :param response: opinion response
        :param is_readonly: is readonly flag; default False
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )
        # check input tag for title
        inputs = soup.find_all(id='id_title')
        self.assertEqual(len(inputs), 1)

        # check textarea tags for content
        inputs = soup.find_all('textarea')
        self.assertEqual(len(inputs), 1)

        # check categories
        category_options = [
            opt for opt in soup.find_all(
                lambda tag: tag.name == 'option'
                and tag.has_attr('selected')
                and tag.parent.name == 'select'
            )]
        for category in [Category.objects.get(name=CATEGORY_UNASSIGNED)]:
            with self.subTest(f'category {category}'):
                tags = list(
                    filter(
                        lambda opt:
                        category.id == int(opt['value']) and
                        category.name == opt.text,
                        category_options
                    )
                )
                self.assertEqual(len(tags), 1)

        # check fieldset is disabled in read only mode
        self.check_tag(self, soup.find_all('fieldset'), is_readonly,
                       lambda tag: tag.has_attr('disabled'))

        # check status only displayed if not read only,
        # i.e. current user's opinion
        found = False
        for span in soup.find_all('span'):
            if TestOpinionView.in_tag_attr(span, 'class', 'badge'):
                found = STATUS_DRAFT == span.text
                if found:
                    break
        if is_readonly:
            self.assertFalse(found)
        else:
            self.assertTrue(found)

        # check submit button only displayed in not read only mode
        tags = soup.find_all(
            lambda tag: tag.name == 'button'
            and TestOpinionView.equal_tag_attr(tag, 'type', 'submit')
        )
        if is_readonly:
            self.assertEqual(len(tags), 0)
        else:
            self.assertEqual(len(tags), 3)
