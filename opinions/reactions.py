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
from typing import Callable, Union, Any

from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import namespaced_url, ensure_list
from .comment_data import CommentBundle, CommentData
from .constants import (
    OPINION_LIKE_ID_ROUTE_NAME,
    OPINION_HIDE_ID_ROUTE_NAME, OPINION_COMMENT_ID_ROUTE_NAME,
    COMMENT_COMMENT_ID_ROUTE_NAME, COMMENT_LIKE_ID_ROUTE_NAME,
    COMMENT_HIDE_ID_ROUTE_NAME, OPINION_PIN_ID_ROUTE_NAME, ALL_FIELDS,
    COMMENT_REPORT_ID_ROUTE_NAME, OPINION_REPORT_ID_ROUTE_NAME,
    OPINION_SLUG_ROUTE_NAME, COMMENT_SLUG_ROUTE_NAME,
    OPINION_FOLLOW_ID_ROUTE_NAME, COMMENT_FOLLOW_ID_ROUTE_NAME,
    COMMENT_ID_ROUTE_NAME
)
from .data_structures import (
    Reaction, ReactionCtrl, HtmlTag, UrlType
)
from .models import Opinion, Comment, AgreementStatus, PinStatus
from .queries import (
    opinion_is_pinned, get_content_status, StatusCheck,
    following_content_author, content_is_hidden, ContentStatus,
    is_content_deleted
)
from .templatetags.reaction_button_id import reaction_button_id
from .enums import ReactionStatus


class ReactionsList:
    """ Reactions list class """
    agree: Reaction        # agree reaction
    disagree: Reaction     # disagree reaction
    comment: Reaction      # disagree reaction
    follow: Reaction       # follow reaction
    unfollow: Reaction     # unfollow reaction
    share: Reaction        # share reaction
    hide: Reaction         # hide reaction
    show: Reaction         # show reaction
    pin: Reaction          # pin reaction
    unpin: Reaction        # unpin reaction
    report: Reaction       # report reaction
    delete: Reaction       # delete reaction
    edit: Reaction         # edit reaction

    AGREE_FIELD = ReactionStatus.AGREE.arg
    DISAGREE_FIELD = ReactionStatus.DISAGREE.arg
    COMMENT_FIELD = ReactionStatus.COMMENT.arg
    FOLLOW_FIELD = ReactionStatus.FOLLOW.arg
    UNFOLLOW_FIELD = ReactionStatus.UNFOLLOW.arg
    SHARE_FIELD = ReactionStatus.SHARE.arg
    HIDE_FIELD = ReactionStatus.HIDE.arg
    SHOW_FIELD = ReactionStatus.SHOW.arg
    PIN_FIELD = ReactionStatus.PIN.arg
    UNPIN_FIELD = ReactionStatus.UNPIN.arg
    REPORT_FIELD = ReactionStatus.REPORT.arg
    DELETE_FIELD = ReactionStatus.DELETE.arg
    EDIT_FIELD = ReactionStatus.EDIT.arg

    AGREE_FIELDS = [AGREE_FIELD, DISAGREE_FIELD]
    FOLLOW_FIELDS = [FOLLOW_FIELD, UNFOLLOW_FIELD]
    HIDE_FIELDS = [HIDE_FIELD, SHOW_FIELD]
    PIN_FIELDS = [PIN_FIELD, UNPIN_FIELD]
    ALL_FIELDS = [
        AGREE_FIELD, DISAGREE_FIELD, COMMENT_FIELD, FOLLOW_FIELD,
        UNFOLLOW_FIELD, SHARE_FIELD, HIDE_FIELD, SHOW_FIELD, PIN_FIELD,
        UNPIN_FIELD, REPORT_FIELD, DELETE_FIELD, EDIT_FIELD
    ]

    def __init__(self, **kwargs):
        for field in ReactionsList.ALL_FIELDS:
            setattr(self, field,
                    kwargs[field] if field in kwargs else Reaction.empty())


COMMENT_MODAL_ID = 'id--comment-modal'
REPORT_MODAL_ID = 'id--report-modal'
HIDE_MODAL_ID = 'id--hide-modal'
SHARE_MODAL_ID = 'id--share-modal'


AGREE_TEMPLATE = Reaction.ajax_of(
    name="Agree", identifier="to-set", icon="", aria="to-set", url="to-set",
    url_type=UrlType.ID, option=ReactionStatus.AGREE.arg,
    field=ReactionsList.AGREE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-hands-clapping"))
DISAGREE_TEMPLATE = Reaction.ajax_of(
    name="Disagree", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.ID, option=ReactionStatus.DISAGREE.arg,
    field=ReactionsList.DISAGREE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-thumbs-down"))
COMMENT_TEMPLATE = Reaction.modal_of(
    name="Comment", identifier="to-set", icon="", aria="to-set", url="to-set",
    url_type=UrlType.ID, modal=f"#{COMMENT_MODAL_ID}",
    field=ReactionsList.COMMENT_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-comment"))
FOLLOW_TEMPLATE = Reaction.ajax_of(
    name="Follow opinion author", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.ID, option=ReactionStatus.FOLLOW.arg,
    field=ReactionsList.FOLLOW_FIELD, group="to-set"
).set_icon(HtmlTag.i(clazz="fa-solid fa-user-tag"))
UNFOLLOW_TEMPLATE = Reaction.ajax_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.ID, option=ReactionStatus.UNFOLLOW.arg,
    field=ReactionsList.UNFOLLOW_FIELD, group="to-set"
).set_icon(HtmlTag.i(clazz="fa-solid fa-user-xmark"))
SHARE_TEMPLATE = Reaction.modal_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.SLUG, modal=f"#{SHARE_MODAL_ID}",
    field=ReactionsList.SHARE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-share-nodes"))
HIDE_TEMPLATE = Reaction.modal_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.ID, option=ReactionStatus.HIDE.arg,
    modal=f"#{HIDE_MODAL_ID}", field=ReactionsList.HIDE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-eye-slash"))
SHOW_TEMPLATE = Reaction.modal_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.ID, option=ReactionStatus.SHOW.arg,
    modal=f"#{HIDE_MODAL_ID}", field=ReactionsList.SHOW_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-eye"))
REPORT_TEMPLATE = Reaction.modal_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", url_type=UrlType.ID, modal=f"#{REPORT_MODAL_ID}",
    field=ReactionsList.REPORT_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-person-military-pointing"))


OPINION_REACTIONS_LIST = ReactionsList(
    agree=AGREE_TEMPLATE.copy(
        identifier=f"{ReactionStatus.AGREE.arg}-opinion",
        aria="Agree with opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME)),
    disagree=DISAGREE_TEMPLATE.copy(
        identifier=f"{ReactionStatus.DISAGREE.arg}-opinion",
        aria="Disagree with opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME)),
    comment=COMMENT_TEMPLATE.copy(
        identifier=f"{ReactionStatus.COMMENT.arg}-opinion",
        aria="Comment on opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_COMMENT_ID_ROUTE_NAME)),
    follow=FOLLOW_TEMPLATE.copy(
        name="Follow opinion author",
        identifier=f"{ReactionStatus.FOLLOW.arg}-opinion",
        aria="Follow opinion author",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_FOLLOW_ID_ROUTE_NAME)),
    unfollow=UNFOLLOW_TEMPLATE.copy(
        name="Unfollow opinion author",
        identifier=f"{ReactionStatus.UNFOLLOW.arg}-opinion",
        aria="Unfollow opinion author",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_FOLLOW_ID_ROUTE_NAME)),
    share=SHARE_TEMPLATE.copy(
        name="Share opinion",
        identifier=f"{ReactionStatus.SHARE.arg}-opinion",
        aria="Share opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_SLUG_ROUTE_NAME)),
    hide=HIDE_TEMPLATE.copy(
        name="Hide opinion",
        identifier=f"{ReactionStatus.HIDE.arg}-opinion", aria="Hide opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_HIDE_ID_ROUTE_NAME)),
    show=SHOW_TEMPLATE.copy(
        name="Show opinion",
        identifier=f"{ReactionStatus.SHOW.arg}-opinion", aria="Show opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_HIDE_ID_ROUTE_NAME)),
    pin=Reaction.ajax_of(
        name="Pin opinion", identifier=f"{ReactionStatus.PIN.arg}-opinion",
        icon="", aria="Pin opinion", url_type=UrlType.ID,
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_PIN_ID_ROUTE_NAME),
        option=ReactionStatus.PIN.arg, field=ReactionsList.PIN_FIELD
    ).set_icon(HtmlTag.i(clazz="fa-solid fa-lock")),
    unpin=Reaction.ajax_of(
        name="Unpin opinion",
        identifier=f"{ReactionStatus.UNPIN.arg}-opinion",
        icon="", aria="Unpin opinion", url_type=UrlType.ID,
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_PIN_ID_ROUTE_NAME),
        option=ReactionStatus.UNPIN.arg, field=ReactionsList.UNPIN_FIELD
    ).set_icon(HtmlTag.i(clazz="fa-solid fa-unlock")),
    report=REPORT_TEMPLATE.copy(
        name="Report opinion",
        identifier=f"{ReactionStatus.REPORT.arg}-opinion",
        aria="Report opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_REPORT_ID_ROUTE_NAME))
)

# list of opinion reaction fields in display order
OPINION_REACTION_FIELDS = [
    ReactionsList.AGREE_FIELD, ReactionsList.DISAGREE_FIELD,
    ReactionsList.COMMENT_FIELD, ReactionsList.FOLLOW_FIELD,
    ReactionsList.UNFOLLOW_FIELD, ReactionsList.SHARE_FIELD,
    ReactionsList.HIDE_FIELD, ReactionsList.SHOW_FIELD,
    ReactionsList.PIN_FIELD, ReactionsList.UNPIN_FIELD,
    ReactionsList.REPORT_FIELD
]
# list of opinion reactions in display order
OPINION_REACTIONS = [
    getattr(OPINION_REACTIONS_LIST, field)
    for field in OPINION_REACTION_FIELDS
]

COMMENT_REACTIONS_LIST = ReactionsList(
    agree=AGREE_TEMPLATE.copy(
        identifier=f"{ReactionStatus.AGREE.arg}-comment",
        aria="Agree with comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME)),
    disagree=DISAGREE_TEMPLATE.copy(
        identifier=f"{ReactionStatus.DISAGREE.arg}-comment",
        aria="Disagree with comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME)),
    comment=COMMENT_TEMPLATE.copy(
        identifier=f"{ReactionStatus.COMMENT.arg}-comment",
        aria="Comment on comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_COMMENT_ID_ROUTE_NAME)),
    follow=FOLLOW_TEMPLATE.copy(
        name="Follow comment author",
        identifier=f"{ReactionStatus.FOLLOW.arg}-comment",
        aria="Follow comment author",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_FOLLOW_ID_ROUTE_NAME)),
    unfollow=UNFOLLOW_TEMPLATE.copy(
        name="Unfollow comment author",
        identifier=f"{ReactionStatus.UNFOLLOW.arg}-comment",
        aria="Unfollow comment author",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_FOLLOW_ID_ROUTE_NAME)),
    share=SHARE_TEMPLATE.copy(
        name="Share comment",
        identifier=f"{ReactionStatus.SHARE.arg}-comment",
        aria="Share comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_SLUG_ROUTE_NAME)),
    hide=HIDE_TEMPLATE.copy(
        name="Hide comment", identifier=f"{ReactionStatus.HIDE.arg}-comment",
        aria="Hide comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_HIDE_ID_ROUTE_NAME)),
    show=SHOW_TEMPLATE.copy(
        name="Show comment", identifier=f"{ReactionStatus.SHOW.arg}-comment",
        aria="Show comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_HIDE_ID_ROUTE_NAME)),
    report=REPORT_TEMPLATE.copy(
        name="Report comment",
        identifier=f"{ReactionStatus.REPORT.arg}-comment",
        aria="Report comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_REPORT_ID_ROUTE_NAME)),
    delete=Reaction.ajax_of(
        name="Delete comment",
        identifier=f"{ReactionStatus.DELETE.arg}-comment",
        icon="", aria="Delete comment", url_type=UrlType.ID,
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_ID_ROUTE_NAME),
        option=ReactionStatus.DELETE.arg, field=ReactionsList.DELETE_FIELD
    ).set_icon(HtmlTag.i(clazz="fa-solid fa-trash-can")),
    edit=Reaction.ajax_of(
        name="Edit comment",
        identifier=f"{ReactionStatus.EDIT.arg}-comment",
        icon="", aria="Edit comment", url_type=UrlType.ID,
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_ID_ROUTE_NAME),
        option=ReactionStatus.EDIT.arg, field=ReactionsList.EDIT_FIELD
    ).set_icon(HtmlTag.i(clazz="fa-solid fa-pen")),
)

# list of comment reaction fields in display order
COMMENT_REACTION_FIELDS = [
    ReactionsList.AGREE_FIELD, ReactionsList.DISAGREE_FIELD,
    ReactionsList.COMMENT_FIELD, ReactionsList.FOLLOW_FIELD,
    ReactionsList.UNFOLLOW_FIELD, ReactionsList.SHARE_FIELD,
    ReactionsList.HIDE_FIELD, ReactionsList.SHOW_FIELD,
    ReactionsList.REPORT_FIELD, ReactionsList.DELETE_FIELD,
    ReactionsList.EDIT_FIELD
]
# list of comment reactions in display order
COMMENT_REACTIONS = [
    getattr(COMMENT_REACTIONS_LIST, field)
    for field in COMMENT_REACTION_FIELDS
]

# always available reactions
ALWAYS_AVAILABLE = [
    ReactionsList.COMMENT_FIELD, ReactionsList.SHARE_FIELD
]
# only available to author reactions
AUTHOR_ONLY = [
    ReactionsList.DELETE_FIELD, ReactionsList.EDIT_FIELD
]
# reactions which don't reflect selected status
NON_SELECTABLE = ALWAYS_AVAILABLE.copy()
NON_SELECTABLE.extend(AUTHOR_ONLY)


def get_reaction_status(
    user: User,
    content: Union[Opinion, Comment, CommentData, CommentBundle, list],
    statuses: dict = None, reactions: list[str] = None,
    enablers: dict = None, visibility: dict = None,
    status_by_id: dict[int, ContentStatus] = None
) -> dict:
    """
    Get the reaction status for the specified content
    :param user: current user
    :param content: opinion/comment/comment bundle/comment data or
                list thereof
    :param statuses: statuses dict to update; default None
    :param reactions: list of reactions to retrieve; default all otherwise
                list of ReactionsList.xxx_FIELD
    :param enablers: dict of enable conditions for reactions with
                ReactionsList.xxx_FIELD as key
    :param visibility: dict of visible conditions for reactions  with
                ReactionsList.xxx_FIELD as key; value can be a boolean or
                a function accepting an Opinion/Comment and returning a
                boolean
    :param status_by_id: dict of ContentStatus values with
                Opinion/Comment id as key
    :return: statuses dict
    """
    if statuses is None:
        statuses = {}

    if content:
        content = ensure_list(content)

        for entry in content:
            if isinstance(entry, CommentBundle):
                reaction_kwargs = {
                    'statuses': statuses,
                    'reactions': reactions,
                    'enablers': enablers,
                    'visibility': visibility,
                    'status_by_id': status_by_id
                }
                for cmt in entry.comment_iterable():
                    get_reaction_status(user, cmt, **reaction_kwargs)
            else:
                entry_is_opinion = isinstance(entry, Opinion)
                if entry_is_opinion:
                    # get status for opinion
                    content_field = AgreementStatus.OPINION_FIELD
                    reaction_fields = OPINION_REACTION_FIELDS
                    pin_field = PinStatus.OPINION_FIELD
                    reactions_list = OPINION_REACTIONS_LIST
                else:
                    # get status for comment
                    content_field = AgreementStatus.COMMENT_FIELD
                    reaction_fields = COMMENT_REACTION_FIELDS
                    pin_field = None    # no pin in COMMENT_REACTIONS_LIST
                    reactions_list = COMMENT_REACTIONS_LIST

                if reactions is None:
                    reactions = reaction_fields
                elif isinstance(reactions, str):
                    reactions = [reactions]

                def enablers_check(fld: str):
                    return field_check(enablers, entry, fld)

                def visibility_check(fld: str):
                    return field_check(visibility, entry, fld)

                # set enabled and visibility conditions for reactions
                enabled = {}
                displayer = {}
                deleted = is_content_deleted(entry.lookup_clazz(), entry.id)

                def two_icon_single_display(
                    ctrl_param: list[tuple[ReactionsList, bool, bool]],
                    active_field: str,
                    inactive_field: str,
                    check_func: Callable[[[Opinion, Comment], User], bool]
                ):
                    """
                    Process reaction with 2 separate icons but only 1 is ever
                    displayed
                    :param ctrl_param: list of tuples to control reactions
                    :param active_field: reaction active field
                    :param inactive_field: reaction inactive field
                    :param check_func: function to check status
                    """
                    active = check_func(entry, user=user) \
                        if any_true(displayer, [
                            active_field, inactive_field
                        ]) else False

                    ctrl_param.extend([
                        # reaction, selected, visible
                        (getattr(reactions_list, active_field), active,
                         displayer[active_field] and not active),
                        (getattr(reactions_list, inactive_field), active,
                         displayer[inactive_field] and active),
                    ])

                for field in ReactionsList.ALL_FIELDS:
                    if field in ReactionsList.PIN_FIELDS and \
                            pin_field is None:
                        # False if pin field not in reactions_list
                        enabled[field] = False
                        displayer[field] = False
                    elif field in ALWAYS_AVAILABLE:
                        enabled[field] = not deleted
                        displayer[field] = True
                    elif field in AUTHOR_ONLY:
                        # delete/edit comment via reactions only available to
                        # comment author
                        enabled[field] = \
                            False if entry_is_opinion or deleted else \
                            entry.user == user
                        displayer[field] = enabled[field]
                    else:
                        # False if deleted or,
                        # ContentStatus.view_ok if specified or,
                        # enabler if specified or, True for ALWAYS_AVAILABLE
                        # or disabled for users' own stuff
                        enabled[field] = \
                            False if deleted else \
                            field_check(
                                status_by_id, entry, entry.id,
                                default=ContentStatus.VIEW_OK).view_ok \
                            if status_by_id else \
                            enablers_check(field) if enablers else \
                            True if field in ALWAYS_AVAILABLE else \
                            entry.user != user

                        # visibility if specified or, True for fields in
                        # reactions
                        displayer[field] = \
                            visibility_check(field) if visibility else \
                            field in reactions

                control_param = [
                    # reaction, selected, visible
                    (getattr(reactions_list, field), False, displayer[field])
                    for field in NON_SELECTABLE if field in reactions
                ]

                # get agree & disagree statuses for comment/opinion
                # (2 separate icons)
                agree = False
                disagree = False
                if any_true(displayer, ReactionsList.AGREE_FIELDS):
                    # need to display agree/disagree
                    query = AgreementStatus.objects.filter(**{
                        AgreementStatus.USER_FIELD: user,
                        content_field: entry
                    })
                    if query.exists():
                        agreement = query.first()
                        agree = \
                            agreement.status.name == \
                            ReactionStatus.AGREE.display
                        disagree = \
                            agreement.status.name == \
                            ReactionStatus.DISAGREE.display

                control_param.extend([
                    # reaction, selected, visible
                    (reactions_list.agree, agree,
                     displayer[ReactionsList.AGREE_FIELD]),
                    (reactions_list.disagree, disagree,
                     displayer[ReactionsList.DISAGREE_FIELD]),
                ])

                # get pin status for opinion
                if pin_field is not None:
                    two_icon_single_display(
                        control_param,
                        ReactionsList.PIN_FIELD,
                        ReactionsList.UNPIN_FIELD,
                        opinion_is_pinned
                    )

                # get following status
                two_icon_single_display(
                    control_param,
                    ReactionsList.FOLLOW_FIELD,
                    ReactionsList.UNFOLLOW_FIELD,
                    following_content_author
                )

                # get hidden status
                two_icon_single_display(
                    control_param,
                    ReactionsList.HIDE_FIELD,
                    ReactionsList.SHOW_FIELD,
                    content_is_hidden
                )

                # get reported status
                reported = False
                if any_true(displayer, ReactionsList.REPORT_FIELD):
                    reported = get_content_status(
                        entry, StatusCheck.REPORTED, user=user,
                        current_user=user
                    ).reported

                control_param.extend([
                    # reaction, selected, visible
                    (reactions_list.report, reported,
                     displayer[ReactionsList.REPORT_FIELD]),
                ])

                statuses.update({
                    # key is button id, value is Reaction
                    reaction_button_id(reaction, entry.id):
                        ReactionCtrl(
                            selected=selected,
                            disabled=not enabled[reaction.field],
                            visible=visible)
                        for reaction, selected, visible in control_param
                })

    return statuses


def any_true(dictionary: dict, keys: [str, list[str]]):
    """
    Check if any of the values for the specified keys are true
    :param dictionary: dictionary to check
    :param keys: keys to check
    :return: True if any true
    """
    if isinstance(keys, str):
        keys = [keys]
    truths = list(map(
        lambda fld: dictionary.get(fld, False), keys
    ))
    return any(truths)


def field_check(dictionary: dict, content: Union[Opinion, Comment],
                field: Union[str, int], default: Any = False) -> Any:
    """
    Check the enabled value for a field in the specified dictionary.
    :param dictionary: dict to check
    :param content: content object to pass to check function if field
                    value is callable
    :param field: field name
    :param default: default value; False
    :return:
    """
    result = default
    if dictionary:
        # if all fields is specified use its value
        fld = ALL_FIELDS if ALL_FIELDS in dictionary else field
        if fld in dictionary:
            # get result of check function otherwise use value
            result = dictionary[fld](content) \
                if callable(dictionary[fld]) else dictionary[fld]
    return result
