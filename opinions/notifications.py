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
from django.contrib import messages
from django.http import HttpRequest
from django.template.loader import render_to_string

from opinions.constants import (
    COUNT_CTX, OPINION_REVIEWS_CTX, COMMENT_REVIEWS_CTX, USER_CTX,
    TAGGED_COUNT_CTX
)
from opinions.models import Opinion, Comment
from opinions.queries import (
    followed_author_publications, own_content_status_changes
)
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import app_template_path


TAGGED_AUTHOR_TEMPLATE = app_template_path(
    OPINIONS_APP_NAME, "snippet", "tagged_author_opinions.html")
CONTENT_UPDATES_TEMPLATE = app_template_path(
    OPINIONS_APP_NAME, "snippet", "content_updates_message.html")


def process_login_opinions(request: HttpRequest, user: User):
    """
    Process a user login
    :param user: user which logged in
    :param request: http request
    """
    if user:
        # tagged author new opinions
        query = followed_author_publications(user, since=user.previous_login)

        context = {
            USER_CTX: user,
            TAGGED_COUNT_CTX: query.count() if query else 0
        }

        # content updates
        for key, model in [
            (OPINION_REVIEWS_CTX, Opinion), (COMMENT_REVIEWS_CTX, Comment)
        ]:
            query = own_content_status_changes(
                user, model, since=user.previous_login)
            context[key] = query.count() if query else 0

        context[COUNT_CTX] = \
            context[OPINION_REVIEWS_CTX] + context[COMMENT_REVIEWS_CTX]

        for count, template in [
            (TAGGED_COUNT_CTX, TAGGED_AUTHOR_TEMPLATE),
            (COUNT_CTX, CONTENT_UPDATES_TEMPLATE),
        ]:
            if context[count]:
                messages.info(
                    request, render_to_string(template, context=context)
                )
