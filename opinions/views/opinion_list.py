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
from typing import Type, Callable, Tuple, Optional, Union, List
from string import capwords

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest

from opinions.comment_data import get_popularity_levels
from opinions.constants import (
    STATUS_QUERY, AUTHOR_QUERY, SEARCH_QUERY, PINNED_QUERY,
    TEMPLATE_OPINION_REACTIONS, TEMPLATE_REACTION_CTRLS, CONTENT_STATUS_CTX,
    REPEAT_SEARCH_TERM_CTX, LIST_HEADING_CTX, PAGE_HEADING_CTX, TITLE_CTX,
    POPULARITY_CTX, OPINION_LIST_CTX, STATUS_BG_CTX, FILTER_QUERY,
    REVIEW_QUERY, IS_REVIEW_CTX, IS_FOLLOWING_FEED_CTX, IS_CATEGORY_FEED_CTX,
    FOLLOWED_CATEGORIES_CTX, CATEGORY_QUERY, ALL_CATEGORIES
)
from opinions.data_structures import OpinionData
from opinions.enums import (
    QueryArg, QueryStatus, OpinionSortOrder, Pinned,
    SortOrder, FilterMode
)
from opinions.models import Opinion
from opinions.queries import (
    opinion_is_pinned, content_status_check, followed_author_publications,
    review_content_by_status
)
from opinions.query_params import QuerySetParams
from opinions.reactions import (
    OPINION_REACTIONS, get_reaction_status, ReactionsList
)
from opinions.views.content_list_mixin import ContentListMixin
from opinions.views.opinion_queries import (
    FILTERS_ORDER, ALWAYS_FILTERS, get_lookup
)
from opinions.views.utils import (
    opinion_permission_check, REORDER_REQ_QUERY_ARGS,
    query_search_term, OPINION_LIST_QUERY_ARGS,
    OPTION_SEARCH_QUERY_ARGS, STATUS_BADGES, add_content_no_show_markers,
    FOLLOWED_OPINION_LIST_QUERY_ARGS, QueryOption,
    REVIEW_OPINION_LIST_QUERY_ARGS, CATEGORY_FEED_QUERY_ARGS
)
from soapbox import OPINIONS_APP_NAME
from utils import Crud, app_template_path


class ListTemplate(Enum):
    """ Enum representing possible response template """
    FULL_TEMPLATE = app_template_path(OPINIONS_APP_NAME, 'opinion_list.html')
    """ Whole page template """
    CONTENT_TEMPLATE = app_template_path(
        OPINIONS_APP_NAME, 'opinion_list_content.html')
    """ List-only template for requery """
    FEED_TEMPLATE = app_template_path(OPINIONS_APP_NAME, 'opinion_feed.html')
    """ Opinion feed template (aka home page) """


class OpinionList(LoginRequiredMixin, ContentListMixin):
    """
    Opinion list response
    """
    # inherited from MultipleObjectMixin via ListView
    model = Opinion

    def __init__(self):
        # response template to use
        self.response_template = ListTemplate.FULL_TEMPLATE

        self.initialise()

    def permission_check_func(
            self) -> Callable[[HttpRequest, Crud, bool], bool]:
        """
        Get the permission check function
        :return: permission check function
        """
        return opinion_permission_check

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return OPINION_LIST_QUERY_ARGS

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
        if query_params.get(
            PINNED_QUERY, QueryArg.of(Pinned.IGNORE)
        ).value == Pinned.YES:
            # current users pinned opinions
            title = 'Pinned opinions'
        elif self.is_query_own(query_params):
            # current users opinions by status
            status = query_params.get(
                STATUS_QUERY, QueryArg.of(QueryStatus.DEFAULT)).value
            if isinstance(status, QueryStatus):
                title = 'All my opinions' \
                    if status.display == QueryStatus.ALL.display \
                    else f'My {status.display} opinions'
            else:
                # list of multiple statuses
                title = \
                    f'My ' \
                    f'{", ".join(map(lambda stat: stat.display, status))} ' \
                    f'opinions'
        else:
            title = 'Opinions'

        return {
            TITLE_CTX: title,
            LIST_HEADING_CTX: capwords(title)
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
            get_lookup(query, query_params[query].value, self.user,
                       query_set_params=query_set_params)

        return query_set_params, None

    def apply_queryset_param(
            self, query_set_params: QuerySetParams, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_set_params: QuerySetParams to apply
        """
        self.queryset = query_set_params.apply(
            Opinion.objects.prefetch_related(Opinion.CATEGORIES_FIELD))

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
                OpinionSortOrder.AUTHOR_AZ, OpinionSortOrder.AUTHOR_ZA
            ])
        if not query_params[STATUS_QUERY].value == QueryStatus.ALL:
            # no need for sort by status if only one status
            excludes.extend([
                OpinionSortOrder.STATUS_AZ, OpinionSortOrder.STATUS_ZA
            ])
        self.sort_order = [
            so for so in OpinionSortOrder if so not in excludes
        ]

    def get_sort_order_enum(self) -> Type[SortOrder]:
        """
        Get the subclass-specific SortOrder enum
        :return: SortOrder enum
        """
        return OpinionSortOrder

    def select_template(
            self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        reorder_query = self.is_reorder(query_params)
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

        def is_pinned(opinion: Opinion):
            """ Check if opinion is pinned by current user """
            return opinion_is_pinned(opinion, self.user)

        self.context_std_elements(
            add_content_no_show_markers(context=context)
        )

        context.update({
            POPULARITY_CTX: get_popularity_levels(context[OPINION_LIST_CTX]),
            TEMPLATE_OPINION_REACTIONS: OPINION_REACTIONS,
            TEMPLATE_REACTION_CTRLS: get_reaction_status(
                self.user, list(context[OPINION_LIST_CTX]),
                # display pin/unpin
                reactions=ReactionsList.PIN_FIELDS,
                visibility={
                    ReactionsList.PIN_FIELD: is_pinned,
                    ReactionsList.UNPIN_FIELD: is_pinned
                }
            ),
            CONTENT_STATUS_CTX: [
                content_status_check(opinion, current_user=self.user)
                for opinion in context[OPINION_LIST_CTX]
            ],
            STATUS_BG_CTX: STATUS_BADGES,
            OPINION_LIST_CTX: list(
                map(OpinionData.from_model, context[OPINION_LIST_CTX])
            )
        })
        if len(context[OPINION_LIST_CTX]) == 0:
            # move list heading to page heading as no content
            context[PAGE_HEADING_CTX] = context[LIST_HEADING_CTX]
            del context[LIST_HEADING_CTX]

        return context

    def is_list_only_template(self) -> bool:
        """
        Is the current render template, the list only template
        :return: True if the list only template
        """
        return self.response_template == ListTemplate.CONTENT_TEMPLATE


class OpinionSearch(OpinionList):
    """
    Search Opinion list response
    """

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return OPTION_SEARCH_QUERY_ARGS

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
            TITLE_CTX: 'Opinion search',
            LIST_HEADING_CTX: f"Results of {search_term}",
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

        for key in FILTERS_ORDER:
            value = query_params[key].value
            was_set = query_params[key].was_set

            if value:
                if key in ALWAYS_FILTERS and not was_set:
                    # don't set always applied filter until everything
                    # else is checked
                    continue

                if not query_entered:
                    query_entered = was_set

                get_lookup(
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
            # no query term entered => all opinions,
            # or query term => search

            for key in ALWAYS_FILTERS:
                if query_set_params.key_in_set(key):
                    continue    # always filter was already applied

                value = query_params[key].value
                if value:
                    get_lookup(key, value, self.user,
                               query_set_params=query_set_params)

            self.queryset = query_set_params.apply(
                Opinion.objects.prefetch_related(Opinion.CATEGORIES_FIELD))

        else:
            # invalid query term entered
            self.queryset = Opinion.objects.none()


class OpinionFollowed(OpinionList):
    """
    Followed authors opinion list response
    """

    QS_PARAMS = 'qs_params'

    title_headings = {
        FilterMode.ALL: ('Tagged author opinions',
                         'All Opinions By Tagged Authors'),
        FilterMode.NEW: ('New tagged author opinions',
                         'New Opinions By Tagged Authors')
    }

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return FOLLOWED_OPINION_LIST_QUERY_ARGS

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        title_heading = self.title_headings.get(
            query_params.get(FILTER_QUERY, FilterMode.DEFAULT).value
        )
        return {
            TITLE_CTX: title_heading[0],
            LIST_HEADING_CTX: title_heading[1],
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

        query_kwargs[OpinionFollowed.QS_PARAMS] = \
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
        return followed_author_publications(
            self.user, since=since, as_params=True)

    def apply_queryset_param(
            self, query_set_params: QuerySetParams, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_set_params: QuerySetParams to apply
        """
        qs_params = kwargs.get(OpinionFollowed.QS_PARAMS, None)

        if qs_params and not qs_params.is_none:
            query_set_params.add(qs_params)

            self.queryset = query_set_params.apply(
                Opinion.objects.prefetch_related(Opinion.CATEGORIES_FIELD)
            )
        else:
            # not following anyone
            self.queryset = Opinion.objects.none()


class OpinionInReview(OpinionFollowed):
    """
    Opinions in review list response
    """

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return REVIEW_OPINION_LIST_QUERY_ARGS

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
            title = f'{status.display} opinions'
            heading = capwords(f'All {"my " if is_own else ""}{title}')
        else:
            title = f'New {status.display} opinions'
            heading = capwords(f'{"My " if is_own else ""}{title}')

        return {
            TITLE_CTX: title,
            LIST_HEADING_CTX: heading,
        }

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

        return review_content_by_status(Opinion, statuses, since=since,
                                        as_params=True)


class OpinionFollowedFeed(OpinionFollowed):
    """
    Followed author opinion feed response
    """

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """
        # set filter as all
        query_params[FILTER_QUERY] = QueryArg(FilterMode.ALL, True)

    def select_template(self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        reorder_query = self.is_reorder(query_params)
        self.response_template = ListTemplate.CONTENT_TEMPLATE \
            if reorder_query else ListTemplate.FEED_TEMPLATE

        # inherited from TemplateResponseMixin via ListView
        self.template_name = self.response_template.value

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        return {
            TITLE_CTX: "Following Feed",
            LIST_HEADING_CTX: "Following Feed",
        }

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        super().set_extra_context(query_params)
        self.extra_context.update({
            IS_FOLLOWING_FEED_CTX: True,
            IS_CATEGORY_FEED_CTX: False
        })


class OpinionCategoryFeed(OpinionList):
    """
    Category opinion feed response
    """

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return CATEGORY_FEED_QUERY_ARGS

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """
        # remove category query if set to all as not required
        if self.category_name_lower(query_params) == ALL_CATEGORIES.lower():
            query_params[CATEGORY_QUERY] = QueryArg.of("")

    @staticmethod
    def category_name_lower(
            query_params: dict[str, QueryArg]) -> Optional[str]:
        """
        Get the lowercase category name
        :param query_params: request query
        """
        category_not_specified = QueryArg.of("")
        selected_category = query_params.get(
            CATEGORY_QUERY, category_not_specified)
        return selected_category.value.lower() \
            if selected_category.value else None

    def select_template(self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        reorder_query = self.is_reorder(query_params)
        self.response_template = ListTemplate.CONTENT_TEMPLATE \
            if reorder_query else ListTemplate.FEED_TEMPLATE

        # inherited from TemplateResponseMixin via ListView
        self.template_name = self.response_template.value

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        return {
            TITLE_CTX: "Category Feed",
            LIST_HEADING_CTX: "Category Feed",
        }

    def set_extra_context(self, query_params: dict[str, QueryArg]):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        """
        super().set_extra_context(query_params)

        selected_category = self.category_name_lower(query_params)
        if not selected_category:
            selected_category = ALL_CATEGORIES.lower()

        def cat_obj(name: str) -> object:
            return {
                'name': name,
                'current': name.lower() == selected_category
            }

        categories = [cat_obj(ALL_CATEGORIES)]
        categories.extend([
            cat_obj(category.name) for category in self.user.categories.all()
        ])

        self.extra_context.update({
            IS_FOLLOWING_FEED_CTX: False,
            IS_CATEGORY_FEED_CTX: True,
            FOLLOWED_CATEGORIES_CTX: categories,
        })
