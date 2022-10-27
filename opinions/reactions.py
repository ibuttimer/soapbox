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
from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import namespaced_url
from .comment_data import CommentBundle
from .constants import (
    OPINION_ID_ROUTE_NAME, OPINION_LIKE_ID_ROUTE_NAME,
    OPINION_HIDE_ID_ROUTE_NAME,
    OPINION_COMMENT_ID_ROUTE_NAME,
    COMMENT_COMMENT_ID_ROUTE_NAME, COMMENT_LIKE_ID_ROUTE_NAME,
    COMMENT_HIDE_ID_ROUTE_NAME, OPINION_PIN_ID_ROUTE_NAME, ALL_FIELDS
)
from .data_structures import Reaction, ReactionCtrl, HtmlTag
from .models import Opinion, Comment, AgreementStatus, PinStatus
from .queries import opinion_is_pinned, content_is_reported
from .templatetags.reaction_button_id import reaction_button_id
from .enums import ReactionStatus
from .views_utils import ensure_list

MODAL = "modal"
AJAX = "ajax"


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

    AGREE_FIELD = ReactionStatus.AGREE.arg
    DISAGREE_FIELD = ReactionStatus.DISAGREE.arg
    COMMENT_FIELD = "comment"
    FOLLOW_FIELD = ReactionStatus.FOLLOW.arg
    UNFOLLOW_FIELD = ReactionStatus.UNFOLLOW.arg
    SHARE_FIELD = "share"
    HIDE_FIELD = ReactionStatus.HIDE.arg
    SHOW_FIELD = ReactionStatus.SHOW.arg
    PIN_FIELD = ReactionStatus.PIN.arg
    UNPIN_FIELD = ReactionStatus.UNPIN.arg
    REPORT_FIELD = "report"
    AGREE_FIELDS = [AGREE_FIELD, DISAGREE_FIELD]
    FOLLOW_FIELDS = [FOLLOW_FIELD, UNFOLLOW_FIELD]
    HIDE_FIELDS = [HIDE_FIELD, SHOW_FIELD]
    PIN_FIELDS = [PIN_FIELD, UNPIN_FIELD]
    ALL_FIELDS = [
        AGREE_FIELD, DISAGREE_FIELD, COMMENT_FIELD, FOLLOW_FIELD,
        UNFOLLOW_FIELD, SHARE_FIELD, HIDE_FIELD, SHOW_FIELD, PIN_FIELD,
        UNPIN_FIELD, REPORT_FIELD
    ]

    def __init__(self, **kwargs):
        for field in ReactionsList.ALL_FIELDS:
            setattr(self, field,
                    kwargs[field] if field in kwargs else Reaction.empty())


COMMENT_MODAL_ID = 'id--comment-modal'
REPORT_MODAL_ID = 'id--report-modal'
COMMENT_REACTION_ID = 'comment'     # used to id comment modal button in js

# TODO share/report

AGREE_TEMPLATE = Reaction.ajax_of(
    name="Agree", identifier="to-set", icon="", aria="to-set", url="to-set",
    option=ReactionStatus.AGREE.arg, field=ReactionsList.AGREE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-hands-clapping"))
DISAGREE_TEMPLATE = Reaction.ajax_of(
    name="Disagree", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=ReactionStatus.DISAGREE.arg,
    field=ReactionsList.DISAGREE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-thumbs-down"))
COMMENT_TEMPLATE = Reaction.modal_of(
    name="Comment", identifier="to-set", icon="", aria="to-set", url="to-set",
    option=f"#{COMMENT_MODAL_ID}", field=ReactionsList.COMMENT_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-comment"))
FOLLOW_TEMPLATE = Reaction.ajax_of(
    name="Follow opinion author", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=ReactionStatus.FOLLOW.arg,
    field=ReactionsList.FOLLOW_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-user-tag"))
UNFOLLOW_TEMPLATE = Reaction.ajax_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=ReactionStatus.UNFOLLOW.arg,
    field=ReactionsList.UNFOLLOW_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-user-xmark"))
SHARE_TEMPLATE = Reaction.modal_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=f"#{COMMENT_MODAL_ID}",
    field=ReactionsList.SHARE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-share-nodes"))
HIDE_TEMPLATE = Reaction.ajax_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=ReactionStatus.HIDE.arg,
    field=ReactionsList.HIDE_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-eye-slash"))
SHOW_TEMPLATE = Reaction.ajax_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=ReactionStatus.SHOW.arg,
    field=ReactionsList.SHOW_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-eye"))
REPORT_TEMPLATE = Reaction.modal_of(
    name="to-set", identifier="to-set", icon="", aria="to-set",
    url="to-set", option=f"#{REPORT_MODAL_ID}",
    field=ReactionsList.REPORT_FIELD
).set_icon(HtmlTag.i(clazz="fa-solid fa-person-military-pointing"))


OPINION_REACTIONS_LIST = ReactionsList(
    agree=AGREE_TEMPLATE.copy(
        identifier="agree-opinion", aria="Agree with opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME)),
    disagree=DISAGREE_TEMPLATE.copy(
        identifier="disagree-opinion", aria="Disagree with opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME)),
    comment=COMMENT_TEMPLATE.copy(
        identifier=f"{COMMENT_REACTION_ID}-opinion", aria="Comment on opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_COMMENT_ID_ROUTE_NAME)),
    follow=FOLLOW_TEMPLATE.copy(
        name="Follow opinion author", identifier="follow-opinion",
        aria="Follow opinion author",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME)),
    unfollow=UNFOLLOW_TEMPLATE.copy(
        name="Unfollow opinion author", identifier="unfollow-opinion",
        aria="Unfollow opinion author",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME)),
    share=SHARE_TEMPLATE.copy(
        name="Share opinion", identifier="share-opinion",
        aria="Share opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME)),
    hide=HIDE_TEMPLATE.copy(
        name="Hide opinion", identifier="hide-opinion", aria="Hide opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_HIDE_ID_ROUTE_NAME)),
    show=SHOW_TEMPLATE.copy(
        name="Show opinion", identifier="show-opinion", aria="Show opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_HIDE_ID_ROUTE_NAME)),
    pin=Reaction.ajax_of(
        name="Pin opinion", identifier="pin-opinion",
        icon="", aria="Pin opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_PIN_ID_ROUTE_NAME),
        option=ReactionStatus.PIN.arg, field=ReactionsList.PIN_FIELD
    ).set_icon(HtmlTag.i(clazz="fa-solid fa-lock")),
    unpin=Reaction.ajax_of(
        name="Unpin opinion", identifier="unpin-opinion",
        icon="", aria="Unpin opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_PIN_ID_ROUTE_NAME),
        option=ReactionStatus.UNPIN.arg, field=ReactionsList.UNPIN_FIELD
    ).set_icon(HtmlTag.i(clazz="fa-solid fa-unlock")),
    report=REPORT_TEMPLATE.copy(
        name="Report opinion", identifier="report-opinion",
        aria="Report opinion",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME))
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
        identifier="agree-comment", aria="Agree with comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME)),
    disagree=DISAGREE_TEMPLATE.copy(
        identifier="disagree-comment", aria="Disagree with comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME)),
    comment=COMMENT_TEMPLATE.copy(
        identifier=f"{COMMENT_REACTION_ID}-comment",
        aria="Comment on comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_COMMENT_ID_ROUTE_NAME)),
    follow=FOLLOW_TEMPLATE.copy(
        name="Follow comment author", identifier="follow-comment",
        aria="Follow comment author",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME)),
    unfollow=UNFOLLOW_TEMPLATE.copy(
        name="Unfollow comment author", identifier="unfollow-comment",
        aria="Unfollow comment author",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME)),
    share=SHARE_TEMPLATE.copy(
        name="Share comment", identifier="share-comment",
        aria="Share comment",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME)),
    hide=HIDE_TEMPLATE.copy(
        name="Hide comment", identifier="hide-comment", aria="Hide comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_HIDE_ID_ROUTE_NAME)),
    show=SHOW_TEMPLATE.copy(
        name="Show comment", identifier="show-comment", aria="Show comment",
        url=namespaced_url(OPINIONS_APP_NAME, COMMENT_HIDE_ID_ROUTE_NAME)),
    report=REPORT_TEMPLATE.copy(
        name="Report comment", identifier="report-comment",
        aria="Report comment",
        url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME))
)

# list of comment reaction fields in display order
COMMENT_REACTION_FIELDS = [
    ReactionsList.AGREE_FIELD, ReactionsList.DISAGREE_FIELD,
    ReactionsList.COMMENT_FIELD, ReactionsList.FOLLOW_FIELD,
    ReactionsList.UNFOLLOW_FIELD, ReactionsList.SHARE_FIELD,
    ReactionsList.HIDE_FIELD, ReactionsList.SHOW_FIELD,
    ReactionsList.REPORT_FIELD
]
# list of comment reactions in display order
COMMENT_REACTIONS = [
    getattr(COMMENT_REACTIONS_LIST, field)
    for field in COMMENT_REACTION_FIELDS
]

ALWAYS_AVAILABLE = [
    ReactionsList.COMMENT_FIELD, ReactionsList.SHARE_FIELD
]


def get_reaction_status(
            user: User, content: [Opinion, Comment, CommentBundle, list],
            statuses: dict = None, reactions: list[str] = None,
            enablers: dict = None, visibility: dict = None
        ) -> dict:
    """
    Get the reaction status for the specified content
    :param user: current user
    :param content: opinion/comment/comment bundle or list thereof
    :param statuses: statuses dict to update; default None
    :param reactions: list of reactions to retrieve; default all otherwise
                    list of ReactionsList.xxx_FIELD
    :param enablers: dict of enable conditions for reactions
    :param visibility: dict of visible conditions for reactions; value can
                be a boolean or a function accepting an Opinion/Comment and
                returning a boolean
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
                    'visibility': visibility
                }
                # get status for bundle comment
                statuses = get_reaction_status(
                    user, entry.comment, **reaction_kwargs)
                # get statuses for replies to bundle comment
                for reply in entry.comments:
                    statuses = get_reaction_status(
                        user, reply, **reaction_kwargs)
            else:
                if isinstance(entry, Opinion):
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
                for field in ReactionsList.ALL_FIELDS:
                    # enabler if specified, True for ALWAYS_AVAILABLE
                    # or disabled for users' own stuff
                    enabled[field] = enablers_check(field) if enablers else \
                        True if field in ALWAYS_AVAILABLE else \
                        entry.user != user

                    # False if pin field not in reactions_list else
                    # visibility if specified, or True for fields in reactions
                    displayer[field] = False \
                        if pin_field is None and \
                        field in ReactionsList.PIN_FIELDS \
                        else visibility_check(field) if visibility else \
                        field in reactions

                control_param = [
                    # reaction, selected, visible
                    (getattr(reactions_list, field), False, True)
                    for field in ALWAYS_AVAILABLE if field in reactions
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
                # (2 separate icons but only 1 ever displayed)
                if pin_field is not None:
                    pinned = False
                    if any_true(displayer, ReactionsList.PIN_FIELDS):
                        # need to display pin/unpin
                        pinned = opinion_is_pinned(entry, user=user)

                    control_param.extend([
                        # reaction, selected, visible
                        (reactions_list.pin, pinned,
                         displayer[ReactionsList.PIN_FIELD] and not pinned),
                        (reactions_list.unpin, pinned,
                         displayer[ReactionsList.UNPIN_FIELD] and pinned),
                    ])

                # get following status
                # (2 separate icons but only 1 ever displayed)
                following = False
                if any_true(displayer, ReactionsList.FOLLOW_FIELDS):
                    pass

                control_param.extend([
                    # reaction, selected, visible
                    (reactions_list.follow, following,
                     displayer[ReactionsList.FOLLOW_FIELD] and not following),
                    (reactions_list.unfollow, not following,
                     displayer[ReactionsList.UNFOLLOW_FIELD] and following),
                ])

                # get hidden status
                # (2 separate icons but only 1 ever displayed)
                hidden = False
                if any_true(displayer, ReactionsList.HIDE_FIELDS):
                    pass

                control_param.extend([
                    # reaction, selected, visible
                    (reactions_list.hide, hidden,
                     displayer[ReactionsList.HIDE_FIELD] and not hidden),
                    (reactions_list.show, not hidden,
                     displayer[ReactionsList.SHOW_FIELD] and hidden),
                ])

                # get reported status
                reported = False
                if any_true(displayer, ReactionsList.REPORT_FIELD):
                    reported = content_is_reported(entry, user=user).reported

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


def field_check(dictionary: dict, content: [Opinion, Comment],
                field: str, default: bool = False) -> bool:
    result = default
    if dictionary:
        fld = ALL_FIELDS if ALL_FIELDS in dictionary else field
        if fld in dictionary:
            result = dictionary[fld](content) \
                if callable(dictionary[fld]) else dictionary[fld]
    return result
