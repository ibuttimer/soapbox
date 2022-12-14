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
from django.db.models import QuerySet
from django.test import TestCase
from bs4 import BeautifulSoup


class CategoryMixin:
    """
    A mixin to support testing categories with BeautifulSoup
    """

    @staticmethod
    def check_categories(
            test_case: TestCase, soup: BeautifulSoup,
            find_func, filter_func,
            categories: QuerySet,
            msg: str = ''):
        """
        Check that the list of selected categories matches expected
        :param test_case: TestCase instance
        :param soup: BeautifulSoup object
        :param find_func: function to find tags
        :param filter_func: function to filter tags
        :param categories: expected categories
        :param msg: message
        """
        category_options = [
            opt for opt in soup.find_all(find_func)]
        for category in list(categories):
            sub_msg = f'{msg} | category {category}'
            with test_case.subTest(sub_msg):
                tags = list(
                    filter(
                        lambda tag: filter_func(category, tag),
                        category_options
                    )
                )
                test_case.assertEqual(
                    len(tags), 1, f"'{category}': {len(tags)} tags found")

    @staticmethod
    def check_category_options(
            test_case: TestCase, soup: BeautifulSoup,
            categories: QuerySet):
        """
        Check that the list of selected categories in a multi-select
        matches the expected
        :param test_case: TestCase instance
        :param soup: BeautifulSoup object
        :param categories: expected categories
        """
        CategoryMixin.check_categories(
            test_case, soup,
            lambda tag: tag.name == 'option'
            and tag.has_attr('selected') and tag.parent.name == 'select',
            lambda category, opt: category.id == int(opt['value'])
            and category.name == opt.text,
            categories)

    @staticmethod
    def check_category_list(
            test_case: TestCase, soup: BeautifulSoup,
            categories: QuerySet):
        """
        Check that the list of selected categories in a unordered list
        matches the expected
        :param test_case: TestCase instance
        :param soup: BeautifulSoup object
        :param categories: expected categories
        """
        CategoryMixin.check_categories(
            test_case, soup,
            lambda tag: tag.name == 'li' and tag.parent.name == 'ul',
            lambda category, opt: category.name == opt.text,
            categories)
