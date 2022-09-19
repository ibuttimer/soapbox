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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.views import generic

from categories import STATUS_PUBLISHED
from categories.models import Status
from soapbox import OPINIONS_APP_NAME
from utils import Crud, app_template_path
from .constants import ORDER_QUERY, PER_PAGE_QUERY, \
    OPINION_PAGINATION_ON_EACH_SIDE, OPINION_PAGINATION_ON_ENDS
from .models import Opinion
from .views_utils import opinion_list_query_args, permission_check, \
    OpinionSortOrder, OpinionPerPage


class OpinionList(LoginRequiredMixin, generic.ListView):
    """
    Opinion list response
    """
    model = Opinion
    queryset = Opinion.objects. \
        prefetch_related('categories').\
        filter(status=Status.objects.get(name=STATUS_PUBLISHED))

    def get(self, request, *args, **kwargs):
        """
        GET method for Opinion list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        permission_check(request, Crud.READ)

        params = opinion_list_query_args(request)

        # set ordering and template
        order, _ = params[ORDER_QUERY]
        ordering = order.order
        if order not in [OpinionSortOrder.NEWEST, OpinionSortOrder.OLDEST]:
            # secondary sort by newest
            ordering = (ordering, OpinionSortOrder.NEWEST.order)
        self.ordering = ordering

        # set pagination
        per_page, _ = params[PER_PAGE_QUERY]
        self.paginate_by = per_page.arg

        # if a query param was set, it's not full page request
        was_set = False
        for k, v in params.items():
            _, was_set = v
            if was_set:
                break
        self.template_name = app_template_path(
            OPINIONS_APP_NAME,
            'opinion_list_content.html' if was_set else 'opinion_list.html')

        response = super(OpinionList, self). \
            get(request, *args, **kwargs)
        return response

    def get_ordering(self):
        """ Get ordering of list """
        ordering = self.ordering
        if isinstance(ordering, tuple):
            # make primary sort case-insensitive
            # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#django.db.models.query.QuerySet.order_by
            order_list = list(ordering)
            order_list[0] = Lower(order_list[0][1:]).desc() \
                if order_list[0].startswith('-') else Lower(order_list[0])
            ordering = tuple(order_list)
        return ordering

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """
        Get template context
        :param object_list:
        :param kwargs: additional keyword arguments
        :return:
        """
        context = super(OpinionList, self).\
            get_context_data(object_list=object_list, **kwargs)

        # initial ordering if secondary sort
        main_order = self.ordering \
            if isinstance(self.ordering, str) else self.ordering[0]
        context.update({
            'sort_order': list(OpinionSortOrder),
            'selected_sort': list(
                filter(lambda order: order.order == main_order,
                       OpinionSortOrder)
            )[0],
            'per_page': list(OpinionPerPage),
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
            ]
        })

        return context
