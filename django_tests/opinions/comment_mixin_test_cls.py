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
from django.http import HttpResponse

from opinions.constants import (
    COMMENT_ID_ROUTE_NAME, COMMENT_SLUG_ROUTE_NAME, MODE_QUERY
)
from opinions.enums import ViewMode
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url
from .opinion_mixin_test_cls import AccessBy
from ..user.base_user_test_cls import BaseUserTest


class CommentMixin(BaseUserTest):
    """
    Test comment page view
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

    def get_route(self, comment_by: AccessBy):
        """
        Get the comment route
        :param comment_by: method of accessing comment; one of AccessBy
        :returns route name
        """
        return COMMENT_ID_ROUTE_NAME \
            if comment_by == AccessBy.BY_ID else COMMENT_SLUG_ROUTE_NAME

    def get_comment_by_id(
            self, pk: int, mode: ViewMode = None) -> HttpResponse:
        """
        Get the comment page
        :param pk: id of comment
        :param mode: view mode; default None
        """
        return self.get_comment_by(pk, AccessBy.BY_ID, mode=mode)

    def get_comment_by_slug(
            self, slug: str, mode: ViewMode = None) -> HttpResponse:
        """
        Get the comment page
        :param slug: slug of comment
        :param mode: view mode; default None
        """
        return self.get_comment_by(slug, AccessBy.BY_SLUG, mode=mode)

    def get_comment_by(
        self, identifier: [int, str], comment_by: AccessBy,
        mode: ViewMode = None
    ) -> HttpResponse:
        """
        Get the comment page
        :param identifier: comment identifier
        :param comment_by: method of accessing comment; one of AccessBy
        :param mode: view mode; default None
        :returns response
        """
        query_kwargs = {
            MODE_QUERY: mode.arg
        } if isinstance(mode, ViewMode) else {}
        return self.client.get(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, self.get_route(comment_by)),
                args=[identifier], query_kwargs=query_kwargs))

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
        return self.client.delete(
            reverse_q(
                namespaced_url(OPINIONS_APP_NAME, self.get_route(comment_by)),
                args=[identifier]))
