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
from typing import Callable, Any, Type, TypeVar, Union

from django.db.models import Q, QuerySet, Model

from opinions.enums import ChoiceArg
from utils import ModelMixin

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeQuerySetParams = TypeVar("TypeQuerySetParams", bound="QuerySetParams")


class QuerySetParams:
    """ Class representing query params to be applied to a QuerySet """
    and_lookups: dict
    """ AND lookups """
    or_lookups: [Q]
    """ OR lookups """
    qs_funcs: [Callable[[QuerySet], QuerySet]]
    """ Functions to apply additional query terms to query set """
    params: set
    """ Set of query keys """
    all_inclusive: int
    """
    All-inclusive query count e.g. all statuses require no actual query
    """
    is_none: bool
    """ Empty query set flag """

    def __init__(self):
        self.and_lookups = {}
        self.or_lookups = []
        self.qs_funcs = []
        self.params = set()
        self.all_inclusive = 0
        self.is_none = False

    def clear(self):
        """ Clear the query set params """
        self.and_lookups.clear()
        self.or_lookups.clear()
        self.qs_funcs.clear()
        self.params.clear()
        self.all_inclusive = 0
        self.is_none = False

    @property
    def and_count(self):
        """ Count of AND terms """
        return len(self.and_lookups)

    @property
    def or_count(self):
        """ Count of OR terms """
        return len(self.or_lookups)

    @property
    def qs_func_count(self):
        """ Count of functions to apply additional query terms """
        return len(self.qs_funcs)

    @property
    def is_empty(self):
        """ Check if empty i.e. no query terms """
        return self.and_count + self.or_count + self.qs_func_count \
            + self.all_inclusive == 0

    def add_and_lookup(self, key, lookup: str, value: Any):
        """
        Add an AND lookup
        :param key: query key
        :param lookup: lookup term
        :param value: lookup value
        """
        self.and_lookups[lookup] = value
        self.params.add(key)

    def add_and_lookups(self, key, lookups: dict[str, Any]):
        """
        Add an AND lookup
        :param key: query key
        :param lookups: dict with lookup term as key and lookup value
        """
        if isinstance(lookups, dict):
            for lookup, value in lookups.items():
                self.add_and_lookup(key, lookup, value)

    def add(self, query_set_param: TypeQuerySetParams):
        """
        Add lookups from specified QuerySetParams object
        :param query_set_param: object to add from
        """
        if isinstance(query_set_param, QuerySetParams):
            self.and_lookups.update(query_set_param.and_lookups)
            self.or_lookups.extend(query_set_param.or_lookups)
            self.qs_funcs.extend(query_set_param.qs_funcs)
            self.all_inclusive += query_set_param.all_inclusive
            self.params.update(query_set_param.params)

    def add_or_lookup(self, key: str, value: Any):
        """
        Add an OR lookup
        :param key: query key
        :param value: lookup value
        """
        if value:
            self.or_lookups.append(value)
            self.params.add(key)

    def add_qs_func(self, key: str, func: Callable[[QuerySet], QuerySet]):
        """
        Add a query term function
        :param key: query key
        :param func: function to apply term
        """
        if func:
            self.qs_funcs.append(func)
            self.params.add(key)

    def add_all_inclusive(self, key: str):
        """
        Add an all-inclusive query term
        :param key: query key
        """
        self.all_inclusive += 1
        self.params.add(key)

    def key_in_set(self, key):
        """
        Check if a query corresponding to the specified `key` has been added
        :param key: query key
        :return: True if added
        """
        return key in self.params

    def apply(self, query_set: QuerySet) -> QuerySet:
        """
        Apply the lookups and term
        :param query_set: query set to apply to
        :return: updated query set
        """
        if self.is_none:
            query_set = query_set.none()
        else:
            query_set = query_set.filter(
                Q(_connector=Q.OR, *self.or_lookups),
                **self.and_lookups)
            for func in self.qs_funcs:
                query_set = func(query_set)
        return query_set


def choice_arg_query(
    query_set_params: QuerySetParams, name: str,
    choice_arg: Type[ChoiceArg], all_options: ChoiceArg,
    model: Type[Union[Model, ModelMixin]], search_field: str,
    query: str, and_lookup: str
):
    """
    Process a ChoiceArg query
    :param query_set_params: query set params
    :param name: query param
    :param choice_arg: ChoiceArg sub class
    :param all_options: all-inclusive option from `choice_arg`
    :param model: model to search
    :param search_field: field in model to search
    :param query: request query
    :param and_lookup: filed lookup for query
    """
    name = name.lower()
    option = choice_arg.from_arg(name)
    inner_qs = None
    if option is not None:
        # term exactly matches a ChoiceArg arg
        if option == all_options:
            # all options so no need for an actual query term
            query_set_params.add_all_inclusive(query)
        else:
            # get required option
            inner_qs = model.objects.get(**{
                f'{search_field}': option.display
            })
    else:
        # no exact match to ChoiceArg arg, try to match part of search field
        status_param = {
            f'{search_field}__icontains': name
        }
        status_qs = model.objects.filter(**status_param)
        if status_qs.count() == 1:
            # only 1 match, get required option
            inner_qs = model.objects.get(**status_param)
        elif status_qs.count() == 0:
            # TODO no match will result in none result
            pass
        else:
            # TODO multiple matches for status
            # multiple matches
            # https://docs.djangoproject.com/en/4.1/topics/db/queries/#complex-lookups-with-q
            query_set_params.add_or_lookup(
                f'{query}-{name}',
                Q(_connector=Q.OR, **{
                    f'{model.id_field()}':
                        stat.id for stat in status_qs.all()
                })
            )

    if inner_qs is not None:
        query_set_params.add_and_lookup(
            query, and_lookup, inner_qs)
