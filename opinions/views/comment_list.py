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
from enum import Enum
from http import HTTPStatus
from typing import Type, Callable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from opinions.comment_data import (
    CommentData, get_comments_review_status
)
from opinions.comment_utils import (
    get_comment_lookup, COMMENT_ALWAYS_FILTERS, COMMENT_FILTERS_ORDER
)
from opinions.constants import (
    STATUS_QUERY, AUTHOR_QUERY, SEARCH_QUERY, REORDER_QUERY, CONTENT_STATUS_CTX,
    UNDER_REVIEW_CONTENT_CTX,
    UNDER_REVIEW_COMMENT_CONTENT, HIDDEN_CONTENT_CTX, HIDDEN_COMMENT_CONTENT
)
from opinions.contexts.comment import comments_list_context_for_opinion
from opinions.enums import QueryArg, QueryStatus, CommentSortOrder, SortOrder
from opinions.models import Comment
from opinions.query_params import QuerySetParams
from opinions.views.content_list_mixin import ContentListMixin
from opinions.views.utils import (
    comment_list_query_args, comment_permission_check,
    comment_search_query_args, REORDER_REQ_QUERY_ARGS,
    NON_REORDER_COMMENT_LIST_QUERY_ARGS, query_search_term
)
from soapbox import OPINIONS_APP_NAME, GET
from user.models import User
from utils import Crud, app_template_path


class ListTemplate(Enum):
    """ Enum representing possible response template """
    FULL_TEMPLATE = app_template_path(OPINIONS_APP_NAME, 'comment_list.html')
    """ Whole page template """
    CONTENT_TEMPLATE = app_template_path(
        OPINIONS_APP_NAME, 'comment_list_content.html')
    """ List-only template for requery """


class CommentList(LoginRequiredMixin, ContentListMixin):
    """
    Comment list response
    """
    # inherited from MultipleObjectMixin via ListView
    model = Comment

    response_template: ListTemplate
    """ Response template to use """

    def permission_check_func(
            self) -> Callable[[HttpRequest, Crud, bool], bool]:
        """
        Get the permission check function
        :return: permission check function
        """
        return comment_permission_check

    def req_query_args(self) -> Callable[[HttpRequest], dict[str, QueryArg]]:
        """
        Get the request query args function
        :return: request query args function
        """
        return comment_list_query_args

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        # build search term string from values that were set
        # inherited from ContextMixin via ListView
        self.extra_context = {
            "repeat_search_term": query_search_term(
                query_params, exclude_queries=REORDER_REQ_QUERY_ARGS)
        }

    def set_queryset(self, query_params: dict[str, QueryArg], user: User):
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param user: current user
        """
        query_set_params = QuerySetParams()

        for query in NON_REORDER_COMMENT_LIST_QUERY_ARGS:
            get_comment_lookup(query, query_params[query].value, user,
                               query_set_params=query_set_params)

        self.queryset = query_set_params.apply(Comment.objects)

    def set_sort_order_options(self, request: HttpRequest,
                               query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param request: http request
        :param query_params: request query
        :return:
        """
        # select sort order options to display
        excludes = []
        if query_params[AUTHOR_QUERY].was_set_to(request.user.username):
            # no need for sort by author if only one author
            excludes.extend([
                CommentSortOrder.AUTHOR_AZ, CommentSortOrder.AUTHOR_ZA
            ])
        if not query_params[STATUS_QUERY].value == QueryStatus.ALL:
            # no need for sort by status if only one status
            excludes.extend([
                CommentSortOrder.STATUS_AZ, CommentSortOrder.STATUS_ZA
            ])
        self.sort_order = [
            so for so in CommentSortOrder if so not in excludes
        ]

    def get_sort_order_enum(self) -> Type[SortOrder]:
        """
        Get the subclass-specific SortOrder enum
        :return: SortOrder enum
        """
        return CommentSortOrder

    def select_template(
            self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        reorder_query = query_params[REORDER_QUERY].value \
            if REORDER_QUERY in query_params else False
        self.response_template = ListTemplate.CONTENT_TEMPLATE \
            if reorder_query else ListTemplate.FULL_TEMPLATE

        # inherited from TemplateResponseMixin via ListView
        self.template_name = self.response_template.value

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """
        Get template context
        :param object_list:
        :param kwargs: additional keyword arguments
        :return:
        """
        context = super().get_context_data(object_list=object_list, **kwargs)

        comment_bundles = [
            CommentData(comment) for comment in context['object_list']
        ]
        # get review status of comments
        comments_review_status = get_comments_review_status(comment_bundles)

        self.context_std_elements(context)

        context.update({
            'comment_list': comment_bundles,
            CONTENT_STATUS_CTX: comments_review_status,
            UNDER_REVIEW_CONTENT_CTX: UNDER_REVIEW_COMMENT_CONTENT,
            HIDDEN_CONTENT_CTX: HIDDEN_COMMENT_CONTENT,
        })
        return context

    def is_list_only_template(self) -> bool:
        """
        Is the current render template, the list only template
        :return: True if the list only template
        """
        return self.response_template == ListTemplate.CONTENT_TEMPLATE


class CommentSearch(CommentList):
    """
    Search Opinion list response
    """

    def req_query_args(self) -> Callable[[HttpRequest], dict[str, QueryArg]]:
        """
        Get the request query args function
        :return: request query args function
        """
        return comment_search_query_args

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        # build search term string from values that were set
        self.extra_context = {
            "search_term": ', '.join([
                f'{q}: {v.value}'
                for q, v in query_params.items() if v.was_set
            ]),
            "repeat_search_term":
                f'{SEARCH_QUERY}='
                f'{query_params[SEARCH_QUERY].value}'
        }

    def set_queryset(self, query_params: dict[str, QueryArg], user: User):
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param user: current user
        """
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#id4
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups

        query_set_params = QuerySetParams()
        query_entered = False  # query term entered flag

        for key in COMMENT_FILTERS_ORDER:
            value = query_params[key].value
            was_set = query_params[key].was_set

            if value:
                if key in COMMENT_ALWAYS_FILTERS and not was_set:
                    # don't set always applied filter until everything
                    # else is checked
                    continue

                if not query_entered:
                    query_entered = was_set

                get_comment_lookup(
                    key, value, user, query_set_params=query_set_params)

                if key == SEARCH_QUERY and not query_set_params.is_empty:
                    # search is a shortcut filter, if search is specified
                    # nothing else is checked after
                    break

        if not query_entered or not query_set_params.is_empty:
            # no query term entered => all comments,
            # or query term => search

            for key in COMMENT_ALWAYS_FILTERS:
                if key in query_set_params.params:
                    continue    # always filter was already applied

                value = query_params[key].value
                if value:
                    get_comment_lookup(key, value, user,
                                       query_set_params=query_set_params)

            self.queryset = query_set_params.apply(Comment.objects)
        else:
            # invalid query term entered
            self.queryset = Comment.objects.none()


@login_required
@require_http_methods([GET])
def opinion_comments(request: HttpRequest) -> HttpResponse:
    """
    Function view for opinion comments.
    This is the endpoint hit by a request for more comments.
    :param request: http request
    :return:
    """
    comment_permission_check(request, Crud.UPDATE)

    query_params = comment_list_query_args(request)

    context = comments_list_context_for_opinion(query_params, request.user)

    return JsonResponse({
        'html': render_to_string(
            app_template_path(
                OPINIONS_APP_NAME, "snippet", "view_comments.html"),
            context=context,
            request=request)
    }, status=HTTPStatus.OK)
