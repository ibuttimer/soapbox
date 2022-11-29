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
from string import capwords
from typing import Type, Callable, Tuple, Optional, Union, List

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
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
    STATUS_QUERY, AUTHOR_QUERY, SEARCH_QUERY, REORDER_QUERY,
    CONTENT_STATUS_CTX, REPEAT_SEARCH_TERM_CTX, PAGE_HEADING_CTX, TITLE_CTX,
    HTML_CTX, TEMPLATE_COMMENT_REACTIONS, TEMPLATE_REACTION_CTRLS,
    REVIEW_QUERY, IS_REVIEW_CTX
)
from opinions.contexts.comment import comments_list_context_for_opinion
from opinions.enums import QueryArg, QueryStatus, CommentSortOrder, SortOrder
from opinions.models import Comment
from opinions.queries import review_content_by_status
from opinions.query_params import QuerySetParams
from opinions.reactions import (
    COMMENT_REACTIONS, get_reaction_status, ReactionsList
)
from opinions.views.content_list_mixin import ContentListMixin
from opinions.views.utils import (
    comment_permission_check, REORDER_REQ_QUERY_ARGS,
    query_search_term, get_query_args,
    COMMENT_LIST_QUERY_ARGS, COMMENT_SEARCH_QUERY_ARGS,
    add_content_no_show_markers, QueryOption,
    NON_REORDER_COMMENT_LIST_QUERY_ARGS, REVIEW_COMMENT_LIST_QUERY_ARGS
)
from soapbox import OPINIONS_APP_NAME, GET
from utils import Crud, app_template_path


class ListTemplate(Enum):
    """ Enum representing possible response template """
    FULL_TEMPLATE = app_template_path(OPINIONS_APP_NAME, 'comment_list.html')
    """ Whole page template """
    CONTENT_TEMPLATE = app_template_path(
        OPINIONS_APP_NAME, 'comment_list_content.html')
    """ List-only template for requery """


COMMENT_LIST_REACTIONS = [
    ReactionsList.SHARE_FIELD, ReactionsList.DELETE_FIELD,
    ReactionsList.EDIT_FIELD
]


class CommentList(LoginRequiredMixin, ContentListMixin):
    """
    Comment list response
    """
    # inherited from MultipleObjectMixin via ListView
    model = Comment

    def __init__(self):
        # response template to use
        self.response_template = ListTemplate.FULL_TEMPLATE

        self.initialise(non_reorder_args=NON_REORDER_COMMENT_LIST_QUERY_ARGS)

    def permission_check_func(
            self) -> Callable[[HttpRequest, Crud, bool], bool]:
        """
        Get the permission check function
        :return: permission check function
        """
        return comment_permission_check

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return COMMENT_LIST_QUERY_ARGS

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        # build search term string from values that were set
        # inherited from ContextMixin via ListView
        self.extra_context = {
            REPEAT_SEARCH_TERM_CTX: query_search_term(
                query_params, exclude_queries=REORDER_REQ_QUERY_ARGS)
        }
        self.extra_context.update(
            self.get_title_heading(query_params))

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        if self.is_query_own(query_params):
            # current users comments by status
            status = query_params.get(
                STATUS_QUERY, QueryArg(QueryStatus.DEFAULT, False)).value
            if isinstance(status, QueryStatus):
                title = 'All my comments' \
                    if status.display == QueryStatus.ALL.display \
                    else f'My {status.display} comments'
            else:
                # list of multiple statuses
                title = \
                    f'My ' \
                    f'{", ".join(map(lambda stat: stat.display, status))} ' \
                    f'comments'
        else:
            title = 'Comments'

        return {
            TITLE_CTX: title,
            PAGE_HEADING_CTX: capwords(title)
        }

    def set_queryset(
        self, query_params: dict[str, QueryArg],
        query_set_params: QuerySetParams = None
    ) -> Tuple[QuerySetParams, Optional[dict]]:
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param query_set_params: QuerySetParams to update; default None
        :return: tuple of query set params and dict of kwargs to pass to
                apply_queryset_param
        """
        if query_set_params is None:
            query_set_params = QuerySetParams()

        for query in self.valid_req_non_reorder_query_args():
            get_comment_lookup(query, query_params[query].value, self.user,
                               query_set_params=query_set_params)

        return query_set_params, None

    def apply_queryset_param(
            self, query_set_params: QuerySetParams, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_set_params: QuerySetParams to apply
        """
        self.queryset = query_set_params.apply(Comment.objects)

    def set_sort_order_options(self, query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param query_params: request query
        :return:
        """
        # select sort order options to display
        excludes = []
        if query_params[AUTHOR_QUERY].was_set_to(self.user.username):
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
        comments_review_status = get_comments_review_status(
            comment_bundles, current_user=self.user)

        self.context_std_elements(context)

        reaction_ctrls = get_reaction_status(
            self.user, comment_bundles,
            reactions=COMMENT_LIST_REACTIONS,
            # no reactions for opinion preview
            enablers={key: True for key in COMMENT_LIST_REACTIONS})

        context.update({
            'comment_list': comment_bundles,
            CONTENT_STATUS_CTX: comments_review_status,
            TEMPLATE_COMMENT_REACTIONS: COMMENT_REACTIONS,
            TEMPLATE_REACTION_CTRLS: reaction_ctrls,
        })
        add_content_no_show_markers(context=context)
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

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return COMMENT_SEARCH_QUERY_ARGS

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        # build search term string from values that were set
        search_term = ', '.join([
            f'{q}: {v.value}'
            for q, v in query_params.items() if v.was_set
        ])
        self.extra_context = {
            TITLE_CTX: 'Comment search',
            PAGE_HEADING_CTX: f"Results of {search_term}",
            REPEAT_SEARCH_TERM_CTX:
                f'{SEARCH_QUERY}='
                f'{query_params[SEARCH_QUERY].value}'
        }

    def set_queryset(
        self, query_params: dict[str, QueryArg],
        query_set_params: QuerySetParams = None
    ) -> Tuple[QuerySetParams, Optional[dict]]:
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param query_set_params: QuerySetParams to update; default None
        :return: tuple of query set params and dict of kwargs to pass to
                apply_queryset_param
        """
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#id4
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups
        if query_set_params is None:
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
                    key, value, self.user, query_set_params=query_set_params)

                if key == SEARCH_QUERY and not query_set_params.is_empty:
                    # search is a shortcut filter, if search is specified
                    # nothing else is checked after
                    break

        return query_set_params, {
            'query_entered': query_entered,
            'query_params': query_params
        }

    def apply_queryset_param(
            self, query_set_params: QuerySetParams, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_set_params: QuerySetParams to apply
        """
        query_entered = kwargs.get('query_entered', None)
        query_params = kwargs.get('query_params', {})

        if not query_entered or not query_set_params.is_empty:
            # no query term entered => all comments,
            # or query term => search

            for key in COMMENT_ALWAYS_FILTERS:
                if query_set_params.key_in_set(key):
                    continue    # always filter was already applied

                value = query_params[key].value
                if value:
                    get_comment_lookup(key, value, self.user,
                                       query_set_params=query_set_params)

            self.queryset = query_set_params.apply(Comment.objects)
        else:
            # invalid query term entered
            self.queryset = Comment.objects.none()


class CommentInReview(CommentList):
    """
    Comments in review list response
    """

    QS_PARAMS = 'qs_params'

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return REVIEW_COMMENT_LIST_QUERY_ARGS

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        super().set_extra_context(query_params)
        self.extra_context[IS_REVIEW_CTX] = True

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        status = query_params.get(
            REVIEW_QUERY, QueryStatus.REVIEW_QUERY_DEFAULT).value
        is_own = self.is_query_own(query_params)
        if self.get_since(query_params) is None:
            title = f'{status.display} comments'
            heading = capwords(f'All {"my " if is_own else ""}{title}')
        else:
            title = f'New {status.display} comments'
            heading = capwords(f'{"My " if is_own else ""}{title}')

        return {
            TITLE_CTX: title,
            PAGE_HEADING_CTX: heading,
        }

    def set_queryset(
            self, query_params: dict[str, QueryArg],
            query_set_params: QuerySetParams = None
    ) -> Tuple[QuerySetParams, Optional[dict]]:
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param query_set_params: QuerySetParams to update; default None
        :return: tuple of query set params and dict of kwargs to pass to
                apply_queryset_param
        """
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#id4
        # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups
        query_set_params, query_kwargs = super().set_queryset(query_params)
        if query_kwargs is None:
            query_kwargs = {}

        query_kwargs[CommentInReview.QS_PARAMS] = \
            self.get_queryset_params(query_params)

        return query_set_params, query_kwargs

    def get_queryset_params(
            self, query_params: dict[str, QueryArg]
    ) -> Optional[Union[QuerySet, QuerySetParams]]:
        """
        Get the queryset to get the list of items for this view
        :param query_params: request query
        :return: query set params
        """
        since = self.get_since(query_params)

        statuses = query_params.get(
            REVIEW_QUERY, QueryStatus.REVIEW_QUERY_DEFAULT).value.listing()

        return review_content_by_status(Comment, statuses, since=since,
                                        as_params=True)

    def apply_queryset_param(
            self, query_set_params: QuerySetParams, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_set_params: QuerySetParams to apply
        """
        qs_params = kwargs.get(CommentInReview.QS_PARAMS, None)

        if qs_params and not qs_params.is_none:
            query_set_params.add(qs_params)

            self.queryset = query_set_params.apply(Comment.objects)
        else:
            # not following anyone
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
        HTML_CTX: render_to_string(
            app_template_path(
                OPINIONS_APP_NAME, "snippet", "view_comments.html"),
            context=context,
            request=request)
    }, status=HTTPStatus.OK)


def comment_list_query_args(request: HttpRequest) -> dict[str, QueryArg]:
    """
    Get comment list query arguments from request query
    :param request: http request
    :return: dict of key query and value (QueryArg | int | str)
    """
    return get_query_args(request, COMMENT_LIST_QUERY_ARGS)
