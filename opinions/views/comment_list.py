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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.http import require_http_methods

from opinions.contexts.comment import comments_list_context_for_opinion
from soapbox import OPINIONS_APP_NAME, GET
from user.models import User
from utils import Crud, app_template_path
from opinions.comment_data import (
    CommentData, get_comments_review_status
)
from opinions.comment_utils import (
    get_comment_lookup, COMMENT_ALWAYS_FILTERS, COMMENT_FILTERS_ORDER
)
from opinions.constants import (
    ORDER_QUERY, STATUS_QUERY, PER_PAGE_QUERY,
    AUTHOR_QUERY, OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS,
    SEARCH_QUERY, REORDER_QUERY, DESC_LOOKUP, DATE_NEWEST_LOOKUP,
    CONTENT_STATUS_CTX, UNDER_REVIEW_CONTENT_CTX,
    UNDER_REVIEW_COMMENT_CONTENT, HIDDEN_CONTENT_CTX, HIDDEN_COMMENT_CONTENT
)
from opinions.models import Comment, is_id_lookup
from opinions.query_params import QuerySetParams
from opinions.views.utils import (
    comment_list_query_args, comment_permission_check,
    comment_search_query_args, REORDER_REQ_QUERY_ARGS,
    NON_REORDER_COMMENT_LIST_QUERY_ARGS, query_search_term
)
from opinions.enums import QueryArg, QueryStatus, CommentSortOrder, PerPage


class ListTemplate(Enum):
    """ Enum representing possible response template """
    FULL_TEMPLATE = app_template_path(OPINIONS_APP_NAME, 'comment_list.html')
    CONTENT_TEMPLATE = app_template_path(
        OPINIONS_APP_NAME, 'comment_list_content.html')


# TODO refactor Opinion and Comment list/search

class CommentList(LoginRequiredMixin, generic.ListView):
    """
    Comment list response
    """
    model = Comment

    response_template: ListTemplate
    """ Response template to use """

    sort_order: list[CommentSortOrder]
    """ Sort order options to display """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        comment_permission_check(request, Crud.READ)

        # TODO currently '/"/= can't be used in content
        # as search depends on them
        query_params = comment_list_query_args(request)

        # build search term string from values that were set
        self.extra_context = {
            "repeat_search_term": query_search_term(
                query_params, exclude_queries=REORDER_REQ_QUERY_ARGS)
        }

        # select sort order options to display
        self.set_sort_order_options(request, query_params)

        # set queryset
        self.set_queryset(query_params, request.user)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super().get(request, *args, **kwargs)

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

    def set_ordering(self, query_params: dict[str, QueryArg]):
        """
        Set the ordering for the response
        :param query_params: request query
        """
        # set ordering
        order = query_params[ORDER_QUERY].value
        ordering = [order.order]    # list of lookups
        if order.to_field() != CommentSortOrder.DEFAULT.to_field():
            # add secondary sort by default sort option
            ordering.append(CommentSortOrder.DEFAULT.order)
        # published date is only set once comment is published so apply an
        # additional orderings: by updated and id
        ordering.append(f'{DATE_NEWEST_LOOKUP}{Comment.UPDATED_FIELD}')
        ordering.append(f'{Comment.ID_FIELD}')
        self.ordering = tuple(ordering)

    def set_pagination(
            self, query_params: dict[str, QueryArg]):
        """
        Set pagination for the response
        :param query_params: request query
        """
        # set pagination
        self.paginate_by = query_params[PER_PAGE_QUERY].value_arg_or_value

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

        self.template_name = self.response_template.value

    def get_ordering(self):
        """ Get ordering of list """
        ordering = self.ordering
        if isinstance(ordering, tuple):
            # make primary sort case-insensitive
            # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#django.db.models.query.QuerySet.order_by
            def insensitive_order(order: str):
                """ Make text orderings case-insensitive """
                non_text = Comment.is_date_lookup(order) or is_id_lookup(order)
                return \
                    order if non_text else \
                    Lower(order[1:]).desc() \
                    if order.startswith(DESC_LOOKUP) else Lower(order)
            ordering = tuple(
                map(insensitive_order, ordering))
        return ordering

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

        # initial ordering if secondary sort
        main_order = self.ordering \
            if isinstance(self.ordering, str) else self.ordering[0]
        context.update({
            'sort_order': self.sort_order,
            'selected_sort': list(
                filter(lambda order: order.order == main_order,
                       CommentSortOrder)
            )[0],
            'per_page': list(PerPage),
            'selected_per_page': self.paginate_by,
            'page_range': [{
                'page_num': page,
                'disabled': page == Paginator.ELLIPSIS,
                'href':
                    f"?page={page}" if page != Paginator.ELLIPSIS else '#',
                'label':
                    f"page {page}" if page != Paginator.ELLIPSIS else '',
                'hidden': f'{bool(page != Paginator.ELLIPSIS)}',
            } for page in context['paginator'].get_elided_page_range(
                number=context['page_obj'].number,
                on_each_side=OPINION_PAGINATION_ON_EACH_SIDE,
                on_ends=OPINION_PAGINATION_ON_ENDS)
            ],
            'comment_list': comment_bundles,
            CONTENT_STATUS_CTX: comments_review_status,
            UNDER_REVIEW_CONTENT_CTX: UNDER_REVIEW_COMMENT_CONTENT,
            HIDDEN_CONTENT_CTX: HIDDEN_COMMENT_CONTENT,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        # return 204 for no content
        if self.response_template == ListTemplate.CONTENT_TEMPLATE and \
                len(context['object_list']) == 0:
            response_kwargs['status'] = HTTPStatus.NO_CONTENT

        return super().render_to_response(context, **response_kwargs)


class CommentSearch(CommentList):
    """
    Search Opinion list response
    """

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        GET method for Opinion search list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        comment_permission_check(request, Crud.READ)

        # Note: values must be in quotes for search query
        query_params = comment_search_query_args(request)

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

        # select sort order options to display
        self.set_sort_order_options(request, query_params)

        # set the query
        self.set_queryset(query_params, request.user)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super(CommentList, self). \
            get(request, *args, **kwargs)

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
