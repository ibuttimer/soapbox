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

from datetime import datetime
from enum import Enum
from typing import Any

from zoneinfo import ZoneInfo

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.template.defaultfilters import truncatechars
from bs4 import BeautifulSoup

from soapbox import OPINIONS_APP_NAME
from utils import permission_name, Crud, app_template_path
from categories import (
    STATUS_DRAFT, STATUS_PUBLISHED, STATUS_PREVIEW, CATEGORY_UNASSIGNED
)
from categories.models import Status, Category
from user.models import User
from .constants import ORDER_QUERY, STATUS_QUERY, PER_PAGE_QUERY, PAGE_QUERY
from .models import Opinion
from .forms import OpinionForm

READ_ONLY = 'read_only'     # read-only mode


class QueryStatus(Enum):
    """ Enum representing status query params """
    DRAFT = 'draft'
    PUBLISH = 'publish'
    PREVIEW = 'preview'


def get_context(title: str,
                submit_url: str = None,
                form: OpinionForm = None, opinion_obj: Opinion = None,
                read_only: bool = False, status: Status = None) -> dict:
    """
    Generate the context for the template
    :param title: title
    :param submit_url: form commit url, default None
    :param form: form to display, default None
    :param opinion_obj: opinion object, default None
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    if status is None:
        status = STATUS_DRAFT

    status_text = status if isinstance(status, str) else status.name

    context = {
        'title': title,
        READ_ONLY: read_only,
        'status': status_text,
        'status_bg':
            'bg-primary' if status_text == STATUS_DRAFT else 'bg-success',
    }

    if form is not None:
        context['form'] = form
        context['submit_url'] = submit_url

    if opinion_obj is not None:
        context['opinion'] = opinion_obj

    return context


def timestamp_opinion(opinion: Opinion):
    """
    Update opinion timestamps
    :param opinion: opinion to update
    """
    timestamp = datetime.now(tz=ZoneInfo("UTC"))
    opinion.updated = timestamp
    if opinion.status == Status.objects.get(name=STATUS_PUBLISHED):
        if opinion.published.year == 1:
            # first time published
            opinion.published = timestamp


def opinion_save_query_args(
        request: HttpRequest) -> tuple[Status, QueryStatus]:
    """
    Get opinion save query arguments from request query
    :param request: http request
    :return: tuple of Status and QueryStatus
    """
    # query params are in request.GET
    # maybe slightly unorthodox, but saves defining 3 routes
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    status = STATUS_DRAFT
    query = QueryStatus.DRAFT
    if STATUS_QUERY in request.GET:
        req_status = request.GET[STATUS_QUERY].lower()
        for status_name, query_opt in [
            (STATUS_PUBLISHED, QueryStatus.PUBLISH),
            (STATUS_PREVIEW, QueryStatus.PREVIEW)
        ]:
            if req_status == query_opt.name.lower():
                status = status_name
                query = query_opt
                break

    status = Status.objects.get(name=status)

    return status, query


class OpinionArg(Enum):
    """ Enum representing opinion sort orders """

    def __init__(self, display: str, arg: Any):
        self.display = display
        self.arg = arg


class OpinionSortOrder(OpinionArg):
    """ Enum representing opinion sort orders """
    NEWEST = ('Newest first', 'new', f'-{Opinion.PUBLISHED_FIELD}')
    OLDEST = ('Oldest first', 'old', f'{Opinion.PUBLISHED_FIELD}')
    AUTHOR_AZ = ('Author A-Z', 'aaz',
                 f'{Opinion.USER_FIELD}__{User.USERNAME_FIELD}')
    AUTHOR_ZA = ('Author Z-A', 'aza',
                 f'-{Opinion.USER_FIELD}__{User.USERNAME_FIELD}')
    TITLE_AZ = ('Title A-Z', 'taz', f'{Opinion.TITLE_FIELD}')
    TITLE_ZA = ('Title Z-A', 'tza', f'-{Opinion.TITLE_FIELD}')

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg)
        self.order = order


OpinionSortOrder.DEFAULT = OpinionSortOrder.NEWEST


class OpinionPerPage(OpinionArg):
    """ Enum representing opinions per page """
    SIX = 6
    NINE = 9
    TWELVE = 12
    FIFTEEN = 15

    def __init__(self, count: int):
        super().__init__(f'{count} per page', count)


OpinionPerPage.DEFAULT = OpinionPerPage.SIX


def opinion_list_query_args(
        request: HttpRequest) -> dict[tuple[OpinionSortOrder, bool]]:
    """
    Get opinion list query arguments from request query
    :param request: http request
    :return: dict of tuples of OpinionSortOrder and QueryStatus
    """
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = {}

    for query, clazz, default in [
        (ORDER_QUERY, OpinionSortOrder, OpinionSortOrder.DEFAULT),
        (PAGE_QUERY, None, 1),
        (PER_PAGE_QUERY, OpinionPerPage, OpinionPerPage.DEFAULT)
    ]:
        params[query] = (default, False)

        if query in request.GET:
            param = request.GET[query].lower()
            default_value = default.arg \
                if isinstance(default, OpinionArg) else default
            if isinstance(default_value, int):
                param = int(param)
            if clazz:
                for opt in clazz:
                    if opt.arg == param:
                        params[query] = (opt, True)
                        break
            else:
                params[query] = (param, True)

    return params


def permission_check(request: HttpRequest, op: Crud):
    """
    Check request user has specified permission
    :param request: http request
    :param op: Crud operation to check
    """
    if not request.user.has_perm(
            permission_name(Opinion, op, app_label=OPINIONS_APP_NAME)):
        raise PermissionDenied("Insufficient permissions")


def own_opinion_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check request user is opinion author
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id:
        raise PermissionDenied(
            "Opinions may only be updated by their authors")


def published_check(request: HttpRequest, opinion_obj: Opinion):
    """
    Check requested opinion is published
    :param request: http request
    :param opinion_obj: opinion
    """
    if request.user.id != opinion_obj.user.id and \
            opinion_obj.status.name != STATUS_PUBLISHED:
        raise PermissionDenied(
            "Opinion unavailable")


def render_form(title: str,
                submit_url: str = None,
                form: OpinionForm = None, opinion_obj: Opinion = None,
                read_only: bool = False, status: Status = None) -> tuple[
        str, dict[str, Opinion | list[str] | OpinionForm | bool]]:
    """
    Render the opinion template
    :param title: title
    :param submit_url: form commit url
    :param form: form to display, default None
    :param opinion_obj: opinion object, default None
    :param read_only: read only flag, default False
    :param status: status, default None
    :return: tuple of template path and context
    """
    context = get_context(
        title, submit_url=submit_url, form=form, opinion_obj=opinion_obj,
        read_only=read_only, status=status
    )
    context.update({
        'summernote_fields': [OpinionForm.CONTENT_FF],
        'other_fields': [OpinionForm.TITLE_FF],
        'category_fields': [OpinionForm.CATEGORIES_FF],
    })

    # set initial data
    form[OpinionForm.CATEGORIES_FF].initial = [
        Category.objects.get(name=CATEGORY_UNASSIGNED)
    ] if opinion_obj is None else opinion_obj.categories.all()

    return app_template_path(OPINIONS_APP_NAME, "opinion_form.html"), context


def generate_excerpt(content: str):
    """
    Generate an excerpt
    :param content: content to generate excerpt from
    :return: excerpt string
    """
    soup = BeautifulSoup(content, features="lxml")
    return truncatechars(
        soup.get_text(), Opinion.OPINION_ATTRIB_EXCERPT_MAX_LEN)
