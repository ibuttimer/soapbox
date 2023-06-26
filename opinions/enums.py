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
from enum import Enum, auto
from string import capwords
from typing import Any, Callable, TypeVar, Optional

from categories.constants import (
    STATUS_ALL, STATUS_DRAFT, STATUS_PUBLISHED, STATUS_PREVIEW,
    STATUS_WITHDRAWN, STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW,
    STATUS_PRE_PUBLISH, STATUS_REVIEW_WIP, STATUS_REVIEW, STATUS_REVIEW_OVER,
    STATUS_UNACCEPTABLE, STATUS_ACCEPTABLE,
    REACTION_AGREE, REACTION_DISAGREE, REACTION_HIDE, REACTION_SHOW,
    REACTION_PIN, REACTION_UNPIN, REACTION_FOLLOW, REACTION_UNFOLLOW,
    REACTION_REPORT, REACTION_SHARE, REACTION_COMMENT, REACTION_DELETE,
    REACTION_EDIT, STATUS_DELETED,
)
from categories.models import Status
from opinions.models import Opinion, Comment
from user.models import User

from utils import DESC_LOOKUP, DATE_OLDEST_LOOKUP, DATE_NEWEST_LOOKUP


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeChoiceArg = TypeVar("TypeChoiceArg", bound="ChoiceArg")
TypeQueryStatus = TypeVar("TypeQueryStatus", bound="QueryStatus")
TypeOpinionSortOrder = \
    TypeVar("TypeOpinionSortOrder", bound="OpinionSortOrder")
TypeCommentSortOrder = \
    TypeVar("TypeCommentSortOrder", bound="CommentSortOrder")
TypeViewMode = TypeVar("ViewMode", bound="ViewMode")
TypeQueryArg = TypeVar("QueryArg", bound="QueryArg")


# https://www.compart.com/en/unicode/block/U+2190
_ARROW_UP = "\N{Upwards Paired Arrows}"
_ARROW_DOWN = "\N{Downwards Paired Arrows}"


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
    def _find_value(
            cls, arg: Any, func: Callable = None) -> Optional[TypeChoiceArg]:
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
    def from_arg(
            cls, arg: Any, func: Callable = None) -> Optional[TypeChoiceArg]:
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
    def from_display(
        cls, display: str, func: Callable = None
    ) -> Optional[TypeChoiceArg]:
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
            display_func = cls._lower_str
        else:
            display_func = cls._pass_thru

        return cls._find_value(display_func(display), func=func)

    @staticmethod
    def arg_if_choice_arg(obj):
        """
        Get the value if `obj` is a ChoiceArg, otherwise `obj`
        :param obj: object to get value of
        :return: value
        """
        return obj.arg \
            if isinstance(obj, ChoiceArg) else obj


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
    def value_arg_or_value(self) -> Any:
        """
        Get the arg value if this object's value is a ChoiceArg, otherwise
        this object's value
        :return: value
        """
        return self.value.arg \
            if isinstance(self.value, ChoiceArg) else self.value

    @staticmethod
    def value_arg_or_object(obj) -> Any:
        """
        Get the arg value if `obj` is a ChoiceArg, otherwise `obj`
        :param obj: object to get value of
        :return: value
        """
        return ChoiceArg.arg_if_choice_arg(obj.value) \
            if isinstance(obj, QueryArg) else obj

    @staticmethod
    def of(obj) -> TypeQueryArg:
        """
        Get an unset QueryArg with the value 0f `obj`
        :param obj: value
        :return: new QueryArg
        """
        return QueryArg(obj, False)

    def __str__(self):
        return f'{self.value}, was_set {self.was_set}'


QueryArg.NONE = QueryArg.of(None)


class QueryStatus(ChoiceArg):
    """ Enum representing status query params """
    # statuses corresponding to statues in the database
    DRAFT = (STATUS_DRAFT, 'draft')
    PUBLISH = (STATUS_PUBLISHED, 'publish')
    PREVIEW = (STATUS_PREVIEW, 'preview')
    DELETED = (STATUS_DELETED, 'deleted')

    WITHDRAWN = (STATUS_WITHDRAWN, 'withdrawn')
    PENDING_REVIEW = (STATUS_PENDING_REVIEW, 'pending-review')
    UNDER_REVIEW = (STATUS_UNDER_REVIEW, 'under-review')
    UNACCEPTABLE = (STATUS_UNACCEPTABLE, 'unacceptable')
    """ Review approved, content needs work """
    ACCEPTABLE = (STATUS_ACCEPTABLE, 'acceptable')
    """ Review rejected, content ok """

    # statuses corresponding to combinations of multiple database statuses
    ALL = (STATUS_ALL, 'all')
    PRE_PUBLISH = (STATUS_PRE_PUBLISH, 'prepublish')
    REVIEW_WIP = (STATUS_REVIEW_WIP, 'review-wip')
    REVIEW = (STATUS_REVIEW, 'review')
    REVIEW_OVER = (STATUS_REVIEW_OVER, 'review-over')

    @classmethod
    def combination_statuses(cls) -> list[TypeQueryStatus]:
        """ List of combination statuses """
        return [
            QueryStatus.ALL, QueryStatus.PRE_PUBLISH, QueryStatus.REVIEW_WIP,
            QueryStatus.REVIEW, QueryStatus.REVIEW_OVER
        ]

    @classmethod
    def non_combination_statuses(cls) -> list[TypeQueryStatus]:
        """ List of non-combination statuses """
        return [
            qry for qry in QueryStatus
            if qry not in QueryStatus.combination_statuses()
        ]

    @classmethod
    def prepublish_statuses(cls) -> list[TypeQueryStatus]:
        """ List of prepublish statuses """
        return [QueryStatus.DRAFT, QueryStatus.PREVIEW]

    @classmethod
    def review_wip_statuses(cls) -> list[TypeQueryStatus]:
        """ List of review in progress statuses """
        return [QueryStatus.PENDING_REVIEW, QueryStatus.UNDER_REVIEW]

    @classmethod
    def review_statuses(cls) -> list[TypeQueryStatus]:
        """ List of review statuses """
        statuses = [QueryStatus.UNACCEPTABLE]
        statuses.extend(cls.review_over_statuses())
        statuses.extend(cls.review_wip_statuses())
        return statuses

    @classmethod
    def review_over_statuses(cls) -> list[TypeQueryStatus]:
        """ List of review over (i.e. ok to view) statuses """
        return [QueryStatus.WITHDRAWN, QueryStatus.ACCEPTABLE]

    @classmethod
    def review_result_statuses(cls) -> list[TypeQueryStatus]:
        """ List of review result (i.e. review decision) statuses """
        return [QueryStatus.UNACCEPTABLE, QueryStatus.ACCEPTABLE]

    def listing(self) -> list[TypeQueryStatus]:
        """
        Get the list of statuses this status corresponds to
        :return: list of statuses
        """
        if self == QueryStatus.ALL:
            statuses = [QueryStatus.PUBLISH]
            statuses.extend(self.prepublish_statuses())
            statuses.extend(self.review_statuses())
        elif self == QueryStatus.PRE_PUBLISH:
            statuses = self.prepublish_statuses()
        elif self == QueryStatus.REVIEW_WIP:
            statuses = self.review_wip_statuses()
        elif self == QueryStatus.REVIEW:
            statuses = self.review_statuses()
        elif self == QueryStatus.REVIEW_OVER:
            statuses = self.review_over_statuses()
        else:
            statuses = [self]
        return statuses

    @property
    def is_prepublish_status(self):
        """ Is a prepublish status """
        return self in QueryStatus.prepublish_statuses()

    @property
    def is_review_wip_status(self):
        """ Is a review wip status """
        return self in QueryStatus.review_wip_statuses()

    @property
    def is_review_status(self):
        """ Is a review status """
        return self in QueryStatus.review_statuses()

    @property
    def is_review_over_status(self):
        """ Is a review over status """
        return self in QueryStatus.review_over_statuses()

    @property
    def is_review_result_status(self):
        """ Is a review result status """
        return self in QueryStatus.review_result_statuses()

    @classmethod
    def ordinal_list(cls) -> list[TypeQueryStatus]:
        """
        Ordinal list representing the status priority order in ascending
        order
        """
        return [
            QueryStatus.DRAFT, QueryStatus.PREVIEW, QueryStatus.PUBLISH,
            QueryStatus.PENDING_REVIEW, QueryStatus.UNDER_REVIEW,
            QueryStatus.WITHDRAWN, QueryStatus.ACCEPTABLE,
            QueryStatus.UNACCEPTABLE
        ]

    def ordinal(self):
        """
        Get the status priority order ordinal for this object
        :return: -1 if no ordinal value
        """
        try:
            result = self.ordinal_list().index(self)
        except ValueError:
            result = -1
        return result

    def __init__(self, display: str, arg: str):
        super().__init__(display, arg)


QueryStatus.DEFAULT = QueryStatus.PUBLISH
QueryStatus.REVIEW_QUERY_DEFAULT = QueryStatus.REVIEW
QueryStatus.REVIEW_SET_DEFAULT = QueryStatus.PENDING_REVIEW


class ReactionStatus(ChoiceArg):
    """ Enum representing reactions query params """
    AGREE = (REACTION_AGREE, 'agree')
    DISAGREE = (REACTION_DISAGREE, 'disagree')
    HIDE = (REACTION_HIDE, 'hide')
    SHOW = (REACTION_SHOW, 'show')
    PIN = (REACTION_PIN, 'pin')
    UNPIN = (REACTION_UNPIN, 'unpin')
    FOLLOW = (REACTION_FOLLOW, 'follow')
    UNFOLLOW = (REACTION_UNFOLLOW, 'unfollow')
    SHARE = (REACTION_SHARE, 'share')
    REPORT = (REACTION_REPORT, 'report')
    COMMENT = (REACTION_COMMENT, 'comment')
    DELETE = (REACTION_DELETE, 'delete')
    EDIT = (REACTION_EDIT, 'edit')

    def __init__(self, display: str, arg: str):
        super().__init__(display, arg)


class SortOrder(ChoiceArg):
    """ Base enum representing sort orders """

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg)
        self.order = order


class OpinionSortOrder(SortOrder):
    """ Enum representing opinion sort orders """
    NEWEST = (f'{capwords(Opinion.SEARCH_DATE_FIELD)} Date {_ARROW_DOWN}',
              'new', f'{DATE_NEWEST_LOOKUP}{Opinion.SEARCH_DATE_FIELD}')
    OLDEST = (f'{capwords(Opinion.SEARCH_DATE_FIELD)} Date {_ARROW_UP}',
              'old', f'{DATE_OLDEST_LOOKUP}{Opinion.SEARCH_DATE_FIELD}')

    # TODO add sort by updated option

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

    @classmethod
    def date_orders(cls) -> list[TypeOpinionSortOrder]:
        """ List of date-related sort orders """
        return [OpinionSortOrder.NEWEST, OpinionSortOrder.OLDEST]

    @property
    def is_date_order(self) -> bool:
        """ Check if this object is a date-related sort order """
        return self in self.date_orders()

    @classmethod
    def author_orders(cls) -> list[TypeOpinionSortOrder]:
        """ List of author-related sort orders """
        return [OpinionSortOrder.AUTHOR_AZ, OpinionSortOrder.AUTHOR_ZA]

    @property
    def is_author_order(self) -> bool:
        """ Check if this object is an author-related sort order """
        return self in self.author_orders()

    @classmethod
    def title_orders(cls) -> list[TypeOpinionSortOrder]:
        """ List of title-related sort orders """
        return [OpinionSortOrder.TITLE_AZ, OpinionSortOrder.TITLE_ZA]

    @property
    def is_title_order(self) -> bool:
        """ Check if this object is a title-related sort order """
        return self in self.title_orders()

    @classmethod
    def status_orders(cls) -> list[TypeOpinionSortOrder]:
        """ List of status-related sort orders """
        return [OpinionSortOrder.STATUS_AZ, OpinionSortOrder.STATUS_ZA]

    @property
    def is_status_order(self) -> bool:
        """ Check if this object is a status-related sort order """
        return self in self.status_orders()

    def to_field(self) -> str:
        """ Get Opinion field used for sorting """
        return Opinion.USER_FIELD if self.is_author_order else \
            Opinion.TITLE_FIELD if self.is_title_order else \
            Opinion.STATUS_FIELD if self.is_status_order else \
            Opinion.SEARCH_DATE_FIELD


OpinionSortOrder.DEFAULT = OpinionSortOrder.NEWEST


class CommentSortOrder(SortOrder):
    """ Enum representing opinion sort orders """
    NEWEST = (f'{capwords(Comment.SEARCH_DATE_FIELD)} Date {_ARROW_DOWN}',
              'new', f'{DATE_NEWEST_LOOKUP}{Comment.SEARCH_DATE_FIELD}')
    OLDEST = (f'{capwords(Comment.SEARCH_DATE_FIELD)} Date {_ARROW_UP}',
              'old', f'{DATE_OLDEST_LOOKUP}{Comment.SEARCH_DATE_FIELD}')
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

    @classmethod
    def date_orders(cls) -> list[TypeCommentSortOrder]:
        """ List of date-related sort orders """
        return [CommentSortOrder.NEWEST, CommentSortOrder.OLDEST]

    @property
    def is_date_order(self) -> bool:
        """ Check if this object is a date-related sort order """
        return self in self.date_orders()

    @classmethod
    def author_orders(cls) -> list[TypeCommentSortOrder]:
        """ List of author-related sort orders """
        return [CommentSortOrder.AUTHOR_AZ, CommentSortOrder.AUTHOR_ZA]

    @property
    def is_author_order(self) -> bool:
        """ Check if this object is an author-related sort order """
        return self in self.author_orders()

    @classmethod
    def status_orders(cls) -> list[TypeCommentSortOrder]:
        """ List of status-related sort orders """
        return [CommentSortOrder.STATUS_AZ, CommentSortOrder.STATUS_ZA]

    @property
    def is_status_order(self) -> bool:
        """ Check if this object is a status-related sort order """
        return self in self.status_orders()

    def to_field(self) -> str:
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


class Pinned(ChoiceArg):
    """ Enum representing pinned opinions """
    NO = ('Not pinned', 'no')
    YES = ('Pinned', 'yes')
    IGNORE = ('Ignore', 'na')


Pinned.DEFAULT = Pinned.IGNORE


class Report(ChoiceArg):
    """ Enum representing report opinion/comment opinions """
    REPORT = ('Report', 'report')
    PENDING = ('Pending', 'pending')
    UNDER = ('Under', 'under')
    WITHDRAW = ('Withdraw', 'withdraw')
    APPROVE = ('Approve', 'approve')
    REJECT = ('Reject', 'reject')


Report.DEFAULT = Report.REPORT


class ViewMode(ChoiceArg):
    """ Enum representing view mode opinions """
    READ_ONLY = ('Read only', 'read-only')
    EDIT = ('Edit', 'edit')
    PREVIEW = ('Preview', 'preview')
    REVIEW = ('Review', 'review')

    @classmethod
    def non_edit_mode(cls, mode: TypeViewMode) -> bool:
        """
        Check if `mode` is a non-edit mode
        :param mode: view mode to check
        :return: True if non-edit
        """
        return mode in [
            ViewMode.READ_ONLY, ViewMode.PREVIEW, ViewMode.REVIEW
        ]

    @property
    def is_non_edit_mode(self) -> bool:
        """
        Object is a non-edit mode
        :return: True if non-edit
        """
        return self.non_edit_mode(self)


ViewMode.DEFAULT = ViewMode.READ_ONLY


class FilterMode(ChoiceArg):
    """ Enum representing view mode options """
    NEW = ('New', 'new')
    ALL = ('All', 'all')


FilterMode.DEFAULT = FilterMode.ALL


class QueryType(Enum):
    """ Enum representing different query types """
    UNKNOWN = auto()

    DRAFT_OPINIONS = auto()
    PREVIEW_OPINIONS = auto()
    IN_REVIEW_OPINIONS = auto()
    ALL_USERS_OPINIONS = auto()
    PINNED_OPINIONS = auto()
    FOLLOWED_NEW_OPINIONS = auto()
    FOLLOWED_ALL_OPINIONS = auto()
    ALL_OPINIONS = auto()
    SEARCH_OPINIONS = auto()
    CATEGORY_FEED_OPINIONS = auto()
    FOLLOWED_FEED_OPINIONS = auto()
