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
from typing import Union

from django.http import HttpResponse

from opinions import (
    OPINION_ID_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_ROUTE_NAME
)
from opinions.constants import (
    COMMENT_ID_ROUTE_NAME, COMMENT_SLUG_ROUTE_NAME, MODE_QUERY
)
from opinions.enums import ViewMode
from opinions.models import Opinion, Comment
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from ..user.base_user_test import BaseUserTest


class AccessBy(Enum):
    """ Access route class """
    BY_ID = auto()
    BY_SLUG = auto()

    def identifier(self, content: Union[Opinion, Comment]) -> Union[int, str]:
        """
        Get the identifier from `content` as specified by this access
        :param content: content to get identifier for
        :return: identifier
        """
        return content.id if self == AccessBy.BY_ID else content.slug


class OpinionMixin(BaseUserTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

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

    def get_opinion_by_id(
            self, pk: int, mode: ViewMode = None) -> HttpResponse:
        """
        Get the opinion page
        :param pk: id of opinion
        :param mode: view mode; default None
        """
        return self.get_opinion_by(pk, AccessBy.BY_ID, mode=mode)

    def get_opinion_by_slug(
            self, slug: str, mode: ViewMode = None) -> HttpResponse:
        """
        Get the opinion page
        :param slug: slug of opinion
        :param mode: view mode; default None
        """
        return self.get_opinion_by(slug, AccessBy.BY_SLUG, mode=mode)

    def get_opinion_by(
        self, identifier: [int, str], opinion_by: AccessBy,
        mode: ViewMode = None
    ) -> HttpResponse:
        """
        Get the opinion page
        :param identifier: opinion identifier
        :param opinion_by: method of accessing opinion; one of AccessBy
        :param mode: view mode; default None
        :returns response
        """
        query_kwargs = {
            MODE_QUERY: mode.arg
        } if isinstance(mode, ViewMode) else {}
        route = OPINION_ID_ROUTE_NAME \
            if opinion_by == AccessBy.BY_ID else OPINION_SLUG_ROUTE_NAME
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, route),
                args=[identifier], query_kwargs=query_kwargs))

    def get_opinion_preview(self, pk: int) -> HttpResponse:
        """
        Get the opinion preview page
        :param pk: id of opinion
        """
        return self.client.get(
            reverse_q(
                namespaced_url(
                    OPINIONS_APP_NAME, OPINION_PREVIEW_ID_ROUTE_NAME),
                args=[pk]))

    def delete_opinion_by_id(self, pk: int) -> HttpResponse:
        """
        Delete an opinion
        :param pk: id of opinion
        """
        return self.delete_opinion_by(pk, AccessBy.BY_ID)

    def delete_opinion_by_slug(self, slug: str) -> HttpResponse:
        """
        Delete an opinion
        :param slug: slug of opinion
        """
        return self.delete_opinion_by(slug, AccessBy.BY_SLUG)

    def delete_opinion_by(
        self, identifier: [int, str], opinion_by: AccessBy
    ) -> HttpResponse:
        """
        Delete an opinion
        :param identifier: opinion identifier
        :param opinion_by: method of accessing opinion; one of AccessBy
        :returns response
        """
        route = OPINION_ID_ROUTE_NAME \
            if opinion_by == AccessBy.BY_ID else OPINION_SLUG_ROUTE_NAME
        return self.client.delete(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, route),
                args=[identifier]))

    def delete_comment_by_id(self, pk: int) -> HttpResponse:
        """
        Delete an comment
        :param pk: id of comment
        """
        return self.delete_comment_by(pk, AccessBy.BY_ID)

    def delete_comment_by_slug(self, slug: str) -> HttpResponse:
        """
        Delete an comment
        :param slug: slug of comment
        """
        return self.delete_comment_by(slug, AccessBy.BY_SLUG)

    def delete_comment_by(
        self, identifier: [int, str], comment_by: AccessBy
    ) -> HttpResponse:
        """
        Delete an comment
        :param identifier: comment identifier
        :param comment_by: method of accessing comment; one of AccessBy
        :returns response
        """
        route = COMMENT_ID_ROUTE_NAME \
            if comment_by == AccessBy.BY_ID else COMMENT_SLUG_ROUTE_NAME
        return self.client.delete(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, route),
                args=[identifier]))
