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
from typing import Callable

from django.test import TestCase
from bs4 import ResultSet, Tag


class SoupMixin:
    """
    A mixin to support testing with BeautifulSoup
    """

    @staticmethod
    def check_tag(
            test_case: TestCase, tags: ResultSet,
            is_readonly: bool, check_func: Callable):
        """
        Check that a tag matches a condition in read only mode and doesn't
        in not read only mode
        :param test_case: TestCase instance
        :param tags: tags to check
        :param is_readonly: read only mode flag
        :param check_func: function to check condition
        """
        bingo = False
        for tag in tags:
            check_ok = check_func(tag)
            if is_readonly and check_ok:
                bingo = True
            elif not is_readonly and not check_ok:
                bingo = True
            if bingo:
                break
        test_case.assertTrue(bingo)

    @staticmethod
    def find_tag(test_case: TestCase, tags: ResultSet,
                 check_func: Callable) -> Tag:
        """
        Check that a tag matches a condition
        :param test_case: TestCase instance
        :param tags: tags to check
        :param check_func: function to check condition
        """
        found_tag = None
        found = False
        for tag in tags:
            found = check_func(tag)
            if found:
                found_tag = tag
                break
        test_case.assertTrue(found)

        return found_tag

    @staticmethod
    def in_tag_attr(tag: Tag, attr: str, content: str):
        """
        Check that a tag attribute contains specified content
        :param tag: tag
        :param attr: attribute
        :param content: content to check
        :returns True if content in tag attribute
        """
        return tag.has_attr(attr) and content in tag[attr]

    @staticmethod
    def equal_tag_attr(tag: Tag, attr: str, content: str):
        """
        Check that a tag attribute equals specified content
        :param tag: tag
        :param attr: attribute
        :param content: content to check
        :returns True if content in tag attribute
        """
        return tag.has_attr(attr) and content == tag[attr]
