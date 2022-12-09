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
from http import HTTPStatus
from typing import Type, Callable, Tuple, Optional, List

from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse
from django.views import generic

from opinions.constants import (
    ORDER_QUERY, UPDATED_FIELD, PER_PAGE_QUERY,
    OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS, AUTHOR_QUERY,
    FILTER_QUERY, REORDER_QUERY
)
from opinions.enums import SortOrder, QueryArg, PerPage, FilterMode
from opinions.query_params import QuerySetParams
from opinions.views.utils import (
    get_query_args, QueryOption, REORDER_REQ_QUERY_ARGS
)
from utils import Crud, DESC_LOOKUP, DATE_NEWEST_LOOKUP


class ContentListMixin(generic.ListView):
    """ Mixin for content list views """

    def __init__(self):
        # sort order options to display
        self.sort_order = None
        # user which initiated request
        self.user = None
        # query args sent for list request which are not always sent with
        # a reorder request
        self.non_reorder_query_args = None

    def initialise(self, non_reorder_args: List[str] = None):
        """
        Initialise this instance
        (The method resolution order is too extended to use a simple
         super().__init__(). See
         https://docs.python.org/3.10/library/functions.html#super)
        """
        self.non_reorder_query_args = [
            a.query for a in self.valid_req_query_args()
            if a.query not in REORDER_REQ_QUERY_ARGS
        ] if non_reorder_args is None else non_reorder_args

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        self.permission_check_func()(request, Crud.READ)

        self.user = request.user

        # TODO currently '/"/= can't be used in content
        # as search depends on them
        query_params = self.req_query_args()(request)
        self.validate_queryset(query_params)

        # set context extra content
        self.set_extra_context(query_params)

        # select sort order options to display
        self.set_sort_order_options(query_params)

        # set queryset
        query_set_params, query_kwargs = \
            self.set_queryset(query_params)
        self.apply_queryset_param(
            query_set_params, **query_kwargs if query_kwargs else {})

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super().get(request, *args, **kwargs)

    def permission_check_func(
            self) -> Callable[[HttpRequest, Crud, bool], bool]:
        """
        Get the permission check function
        :return: permission check function
        """
        raise NotImplementedError(
            "'permission_check_func' method must be overridden by sub "
            "classes")

    def req_query_args(
            self) -> Callable[[HttpRequest], dict[str, QueryArg]]:
        """
        Get the request query args function
        :return: request query args function
        """
        return lambda request: get_query_args(
            request, self.valid_req_query_args())

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        raise NotImplementedError(
            "'valid_req_query_args' method must be overridden by sub classes")

    def valid_req_non_reorder_query_args(self) -> List[str]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return self.non_reorder_query_args

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """
        pass

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        raise NotImplementedError(
            "'set_extra_content' method must be overridden by sub classes")

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
        raise NotImplementedError(
            "'set_queryset' method must be overridden by sub classes")

    def apply_queryset_param(
            self, query_set_params: QuerySetParams, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_set_params: QuerySetParams to apply
        """
        raise NotImplementedError(
            "'apply_queryset_param' method must be overridden by sub classes")

    def set_sort_order_options(self, query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param query_params: request query
        """
        raise NotImplementedError(
            "'set_sort_order_options' method must be overridden by sub "
            "classes")

    def set_ordering(self, query_params: dict[str, QueryArg]):
        """
        Set the ordering for the response
        :param query_params: request query
        """
        sort_order = self.get_sort_order_enum()

        # set ordering
        order = query_params[ORDER_QUERY].value
        ordering = [order.order]    # list of lookups
        if order.to_field() != sort_order.DEFAULT.to_field():
            # add secondary sort by default sort option
            ordering.append(sort_order.DEFAULT.order)
        # published date is only set once comment is published so apply an
        # additional orderings: by updated and id
        ordering.append(f'{DATE_NEWEST_LOOKUP}{UPDATED_FIELD}')
        ordering.append(f'{self.model.id_field()}')
        # inherited from MultipleObjectMixin via ListView
        self.ordering = tuple(ordering)

    def get_sort_order_enum(self) -> Type[SortOrder]:
        """
        Get the subclass-specific SortOrder enum
        :return: SortOrder enum
        """
        raise NotImplementedError(
            "'url' method must be overridden by sub classes")

    def set_pagination(
            self, query_params: dict[str, QueryArg]):
        """
        Set pagination for the response
        :param query_params: request query
        """
        # set pagination
        # inherited from MultipleObjectMixin via ListView
        self.paginate_by = query_params[PER_PAGE_QUERY].value_arg_or_value

    def get_ordering(self):
        """ Get ordering of list """
        ordering = self.ordering
        if isinstance(ordering, tuple):
            # make primary sort case-insensitive
            # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#django.db.models.query.QuerySet.order_by
            def insensitive_order(order: str):
                """ Make text orderings case-insensitive """
                non_text = self.model.is_date_lookup(order) or \
                    self.model.is_id_lookup(order)
                return \
                    order if non_text else \
                    Lower(order[1:]).desc() \
                    if order.startswith(DESC_LOOKUP) else Lower(order)
            ordering = tuple(
                map(insensitive_order, ordering))
        return ordering

    def context_std_elements(self, context: dict) -> dict:
        """
        Update the specified context with the standard elements:
        - sort order
        - per page
        - pagination
        :param context: context to update
        :return: context
        """
        # initial ordering if secondary sort
        main_order = self.ordering \
            if isinstance(self.ordering, str) else self.ordering[0]
        context.update({
            'sort_order': self.sort_order,
            'selected_sort': list(
                filter(lambda order: order.order == main_order,
                       self.get_sort_order_enum())
            )[0],
            'per_page': list(PerPage),
            'selected_per_page': self.paginate_by,
            'page_links': [{
                'page_num': page,
                'disabled': page == Paginator.ELLIPSIS,
                'href':
                    f"?page={page}" if page != Paginator.ELLIPSIS else '',
                'label':
                    f"page {page}" if page != Paginator.ELLIPSIS else '',
                'hidden': f'{str(bool(page != Paginator.ELLIPSIS)).lower()}',
            } for page in context['paginator'].get_elided_page_range(
                number=context['page_obj'].number,
                on_each_side=OPINION_PAGINATION_ON_EACH_SIDE,
                on_ends=OPINION_PAGINATION_ON_ENDS)
            ]
        })
        return context

    def select_template(self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        raise NotImplementedError(
            "'select_template' method must be overridden by sub classes")

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        # return 204 for no content
        if self.is_list_only_template() and len(context['object_list']) == 0:
            response_kwargs['status'] = HTTPStatus.NO_CONTENT

        return super().render_to_response(context, **response_kwargs)

    def is_list_only_template(self) -> bool:
        """
        Is the current render template, the list only template
        :return: True if the list only template
        """
        raise NotImplementedError(
            "'is_list_only_template' method must be overridden by sub "
            "classes")

    def is_query_own(self, query_params: dict[str, QueryArg]) -> bool:
        """
        Check if query is for rhe current user
        :param query_params: query params
        :return: True is current user is author in query
        """
        author = query_params.get(AUTHOR_QUERY, None)
        return author is not None and author.value == self.user.username

    def get_since(
            self, query_params: dict[str, QueryArg]) -> Optional[datetime]:
        """
        Get the query since date
        :param query_params: request query
        :return: since date or None
        """
        return None if \
            query_params.get(FILTER_QUERY, FilterMode.DEFAULT).value == \
            FilterMode.ALL else self.user.previous_login

    @staticmethod
    def is_reorder(query_params: dict[str, QueryArg]):
        return query_params[REORDER_QUERY].value \
            if REORDER_QUERY in query_params else False
