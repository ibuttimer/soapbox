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
from typing import Any, Callable

from categories import (
    STATUS_DRAFT, STATUS_PUBLISHED, STATUS_PREVIEW, STATUS_WITHDRAWN,
    STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW, STATUS_APPROVED,
    STATUS_REJECTED,
    REACTION_AGREE, REACTION_DISAGREE, REACTION_HIDE, REACTION_SHOW,
    REACTION_FOLLOW, REACTION_UNFOLLOW
)
from categories.constants import STATUS_ALL
from categories.models import Status
from opinions.models import Opinion, Comment
from user.models import User

from .constants import DATE_NEWEST_LOOKUP, DATE_OLDEST_LOOKUP, DESC_LOOKUP


class ChoiceArg(Enum):
    """ Enum representing options with limited choices """
    display: str
    """ Display string """
    arg: Any
    """ Argument value """

    def __init__(self, display: str, arg: Any):
        self.display = display
        self.arg = arg

    @staticmethod
    def _lower_str(val):
        """ Lower string value function for filtering """
        return val.lower() if isinstance(val, str) else val

    @staticmethod
    def _pass_thru(val):
        """ Pass-through filter function """
        return val

    @classmethod
    def _find_value(cls, arg: Any, func: Callable = None):
        """
        Get value matching specified arg
        :param arg: arg to find
        :param func: value transform function to be applied before comparison;
                     default pass-through
        :return: ChoiceArg value or None if not found
        """
        if func is None:
            func = cls._pass_thru

        matches = list(
            filter(
                lambda val: func(val) == arg,
                cls
            )
        )
        return matches[0] if len(matches) == 1 else None

    @classmethod
    def from_arg(cls, arg: Any, func: Callable = None):
        """
        Get value matching specified arg
        :param arg: arg to find
        :param func: value transform function to be applied before comparison;
                     default convert to lower-case string
        :return: ChoiceArg value or None if not found
        """
        if func is None:
            def trans_func(val):
                return cls._lower_str(val.arg)
            func = trans_func

        return cls._find_value(arg, func=func)

    @classmethod
    def from_display(cls, display: str, func: Callable = None):
        """
        Get value matching specified display string
        :param display: display string to find
        :param func: value transform function to be applied before comparison;
                     default convert to lower-case string
        :return: ChoiceArg value or None if not found
        """
        if func is None:
            def trans_func(val):
                return cls._lower_str(val.display)
            func = trans_func

        return cls._find_value(display, func=func)


class QueryArg:
    """ Class representing query args """
    value: Any
    """ Value """
    was_set: bool
    """ Argument was set in request flag """

    def __init__(self, value: Any, was_set: bool):
        self.set(value, was_set)

    def set(self, value: Any, was_set: bool):
        """
        Set the value and was set flag
        :param value:
        :param was_set:
        :return:
        """
        self.value = value
        self.was_set = was_set

    def was_set_to(self, value: Any, attrib: str = None):
        """
        Check if value was to set the specified `value`
        :param value: value to check
        :param attrib: attribute of set value to check; default None
        :return: True if value was to set the specified `value`
        """
        chk_value = self.value if not attrib else getattr(self.value, attrib)
        return self.was_set and chk_value == value

    @property
    def query_arg_value(self):
        """
        Get the arg value of a query argument
        :return: value
        """
        return self.value.arg \
            if isinstance(self.value, ChoiceArg) else self.value

    def __str__(self):
        return f'{self.value}, was_set {self.was_set}'


class QueryStatus(ChoiceArg):
    """ Enum representing status query params """
    ALL = (STATUS_ALL, 'all')
    DRAFT = (STATUS_DRAFT, 'draft')
    PUBLISH = (STATUS_PUBLISHED, 'publish')
    PREVIEW = (STATUS_PREVIEW, 'preview')
    WITHDRAWN = (STATUS_WITHDRAWN, 'withdrawn')
    PENDING_REVIEW = (STATUS_PENDING_REVIEW, 'pending-review')
    UNDER_REVIEW = (STATUS_UNDER_REVIEW, 'under-review')
    APPROVED = (STATUS_APPROVED, 'approved')
    REJECTED = (STATUS_REJECTED, 'rejected')

    def __init__(self, display: str, arg: str):
        super().__init__(display, arg)


class ReactionStatus(ChoiceArg):
    """ Enum representing reactions query params """
    AGREE = (REACTION_AGREE, 'agree')
    DISAGREE = (REACTION_DISAGREE, 'disagree')
    HIDE = (REACTION_HIDE, 'hide')
    SHOW = (REACTION_SHOW, 'show')
    FOLLOW = (REACTION_FOLLOW, 'follow')
    UNFOLLOW = (REACTION_UNFOLLOW, 'unfollow')

    def __init__(self, display: str, arg: str):
        super().__init__(display, arg)


class SortOrder(ChoiceArg):
    """ Base enum representing sort orders """

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg)
        self.order = order


class OpinionSortOrder(SortOrder):
    """ Enum representing opinion sort orders """
    NEWEST = ('Newest first', 'new',
              f'{DATE_NEWEST_LOOKUP}{Opinion.SEARCH_DATE_FIELD}')
    OLDEST = ('Oldest first', 'old',
              f'{DATE_OLDEST_LOOKUP}{Opinion.SEARCH_DATE_FIELD}')
    AUTHOR_AZ = ('Author A-Z', 'aaz',
                 f'{Opinion.USER_FIELD}__{User.USERNAME_FIELD}')
    AUTHOR_ZA = ('Author Z-A', 'aza',
                 f'{DESC_LOOKUP}{Opinion.USER_FIELD}__'
                 f'{User.USERNAME_FIELD}')
    TITLE_AZ = ('Title A-Z', 'taz', f'{Opinion.TITLE_FIELD}')
    TITLE_ZA = ('Title Z-A', 'tza',
                f'{DESC_LOOKUP}{Opinion.TITLE_FIELD}')
    STATUS_AZ = ('Status A-Z', 'saz',
                 f'{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}')
    STATUS_ZA = ('Status Z-A', 'sza',
                 f'{DESC_LOOKUP}{Opinion.STATUS_FIELD}__'
                 f'{Status.NAME_FIELD}')

    @property
    def is_date_order(self):
        return self in [OpinionSortOrder.NEWEST, OpinionSortOrder.OLDEST]

    @property
    def is_author_order(self):
        return self in [
            OpinionSortOrder.AUTHOR_AZ, OpinionSortOrder.AUTHOR_ZA]

    @property
    def is_title_order(self):
        return self in [OpinionSortOrder.TITLE_AZ, OpinionSortOrder.TITLE_ZA]

    @property
    def is_status_order(self):
        return self in [
            OpinionSortOrder.STATUS_AZ, OpinionSortOrder.STATUS_ZA]

    def to_field(self):
        """ Get Opinion field used for sorting """
        return Opinion.USER_FIELD if self.is_author_order else \
            Opinion.TITLE_FIELD if self.is_title_order else \
            Opinion.STATUS_FIELD if self.is_status_order else \
            Opinion.SEARCH_DATE_FIELD


OpinionSortOrder.DEFAULT = OpinionSortOrder.NEWEST


class CommentSortOrder(SortOrder):
    """ Enum representing opinion sort orders """
    NEWEST = ('Newest first', 'new',
              f'{DATE_NEWEST_LOOKUP}{Comment.SEARCH_DATE_FIELD}')
    OLDEST = ('Oldest first', 'old',
              f'{DATE_OLDEST_LOOKUP}{Comment.SEARCH_DATE_FIELD}')
    AUTHOR_AZ = ('Author A-Z', 'aaz',
                 f'{Comment.USER_FIELD}__{User.USERNAME_FIELD}')
    AUTHOR_ZA = ('Author Z-A', 'aza',
                 f'{DESC_LOOKUP}{Comment.USER_FIELD}__'
                 f'{User.USERNAME_FIELD}')
    STATUS_AZ = ('Status A-Z', 'saz',
                 f'{Comment.STATUS_FIELD}__{Status.NAME_FIELD}')
    STATUS_ZA = ('Status Z-A', 'sza',
                 f'{DESC_LOOKUP}{Comment.STATUS_FIELD}__'
                 f'{Status.NAME_FIELD}')

    @property
    def is_date_order(self):
        return self in [CommentSortOrder.NEWEST, CommentSortOrder.OLDEST]

    @property
    def is_author_order(self):
        return self in [
            CommentSortOrder.AUTHOR_AZ, CommentSortOrder.AUTHOR_ZA]

    @property
    def is_status_order(self):
        return self in [
            CommentSortOrder.STATUS_AZ, CommentSortOrder.STATUS_ZA]

    def to_field(self):
        """ Get Comment field used for sorting """
        return Comment.USER_FIELD if self.is_author_order else \
            Comment.STATUS_FIELD if self.is_status_order else \
            Comment.SEARCH_DATE_FIELD


CommentSortOrder.DEFAULT = CommentSortOrder.OLDEST


class PerPage(ChoiceArg):
    """ Enum representing opinions per page """
    SIX = 6
    NINE = 9
    TWELVE = 12
    FIFTEEN = 15

    def __init__(self, count: int):
        super().__init__(f'{count} per page', count)


PerPage.DEFAULT = PerPage.SIX


class Hidden(ChoiceArg):
    """ Enum representing hidden opinions """
    NO = ('Not hidden', 'no')
    YES = ('Hidden', 'yes')
    IGNORE = ('Ignore', 'na')


Hidden.DEFAULT = Hidden.NO