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
from django.template.defaultfilters import pluralize

from opinions.models import Opinion, Comment
from opinions.queries import (
    followed_author_publications, own_content_status_changes
)
from user.models import User
from utils.models import ModelMixin


def process_login_opinions(request: HttpRequest, user: User):
    """
    Process a user login
    :param user: user which logged in
    :param request: http request
    """
    if user:
        query = followed_author_publications(user, since=user.previous_login)
        count = query.count() if query else 0
        if count > 0:
            messages.info(
                request,
                f'{count} opinion{pluralize(count)} '
                f'{"has" if count == 1 else "have"} been published by '
                f'authors you follow since you last logged in.'
            )

        for model in [Opinion, Comment]:
            query = own_content_status_changes(
                user, model, since=user.previous_login)
            count = query.count() if query else 0
            if count > 0:
                messages.info(
                    request,
                    f'{count} '
                    f'{ModelMixin.model_name_obj(model)}{pluralize(count)} '
                    f'{"has" if count == 1 else "have"} been updated since '
                    f'you last logged in.'
                )
