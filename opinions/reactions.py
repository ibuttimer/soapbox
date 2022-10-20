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
from collections import namedtuple

from soapbox import OPINIONS_APP_NAME
from user.models import User
from utils import namespaced_url
from .comment_data import CommentBundle
from .constants import (
    OPINION_ID_ROUTE_NAME, OPINION_LIKE_ID_ROUTE_NAME,
    OPINION_HIDE_ID_ROUTE_NAME,
    OPINION_COMMENT_ID_ROUTE_NAME,
    COMMENT_COMMENT_ID_ROUTE_NAME, COMMENT_LIKE_ID_ROUTE_NAME,
    COMMENT_HIDE_ID_ROUTE_NAME
)
from .data_structures import Reaction, ReactionCtrl
from .models import Opinion, Comment, AgreementStatus
from .templatetags.reaction_button_id import reaction_button_id
from .enums import ReactionStatus

MODAL = "modal"
AJAX = "ajax"

ReactionsList = namedtuple("ReactionsList", [
    "agree",        # agree reaction
    "disagree",     # disagree reaction
    "follow",       # follow reaction
    "hide",         # hide reaction
    "report",       # report reaction
])

COMMENT_MODAL_ID = 'id--comment-modal'
COMMENT_REACTION_ID = 'comment'     # used to id comment modal button in js

# TODO share/report

OPINION_REACTION_AGREE = Reaction(
    name="Agree", id="agree-opinion", icon="fa-solid fa-hands-clapping",
    aria="Agree with opinion", type=AJAX,
    url=namespaced_url(OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME),
    option=ReactionStatus.AGREE.arg
)
OPINION_REACTION_DISAGREE = Reaction(
    name="Disagree", id="disagree-opinion", icon="fa-solid fa-thumbs-down",
    aria="Disagree with opinion", type=AJAX,
    url=namespaced_url(
        OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME),
    option=ReactionStatus.DISAGREE.arg
)
OPINION_REACTION_FOLLOW = Reaction(
    name="Follow author", id="follow-opinion", icon="fa-solid fa-user-tag",
    aria="Follow opinion author", type=AJAX,
    url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
    option=ReactionStatus.FOLLOW.arg
)
OPINION_REACTION_HIDE = Reaction(
    name="Hide opinion", id="hide-opinion", icon="fa-solid fa-eye-slash",
    aria="Hide opinion", type=AJAX,
    url=namespaced_url(OPINIONS_APP_NAME, OPINION_HIDE_ID_ROUTE_NAME),
    option=ReactionStatus.HIDE.arg
)
OPINION_REACTION_REPORT = Reaction(
    name="Report opinion", id="report-opinion",
    icon="fa-solid fa-person-military-pointing",
    aria="Report opinion", type=MODAL,
    url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
    option=f"#{COMMENT_MODAL_ID}"
)
OPINION_REACTIONS_LIST = ReactionsList(
    OPINION_REACTION_AGREE, OPINION_REACTION_DISAGREE,
    OPINION_REACTION_FOLLOW, OPINION_REACTION_HIDE, OPINION_REACTION_REPORT)

OPINION_REACTIONS = [
    OPINION_REACTION_AGREE,
    OPINION_REACTION_DISAGREE,
    Reaction(name="Comment", id=f"{COMMENT_REACTION_ID}-opinion",
             icon="fa-solid fa-comment",
             aria="Comment on opinion", type=MODAL,
             url=namespaced_url(
                 OPINIONS_APP_NAME, OPINION_COMMENT_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-user-xmark"></i> to unfollow
    OPINION_REACTION_FOLLOW,
    Reaction(name="Share opinion", id="share-opinion",
             icon="fa-solid fa-share-nodes",
             aria="Share opinion", type=MODAL,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-eye"></i> to un-hide
    OPINION_REACTION_HIDE,
    OPINION_REACTION_REPORT,
]

COMMENT_REACTION_AGREE = Reaction(
    name="Agree", id="agree-comment", icon="fa-solid fa-hands-clapping",
    aria="Agree with comment", type=AJAX,
    url=namespaced_url(
        OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME),
    option=ReactionStatus.AGREE.arg
)
COMMENT_REACTION_DISAGREE = Reaction(
    name="Disagree", id="disagree-comment", icon="fa-solid fa-thumbs-down",
    aria="Disagree with comment", type=AJAX,
    url=namespaced_url(
        OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME),
    option=ReactionStatus.DISAGREE.arg
)
COMMENT_REACTION_FOLLOW = Reaction(
    name="Follow author", id="follow-comment", icon="fa-solid fa-user-tag",
    aria="Follow comment author", type=AJAX,
    url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
    option=ReactionStatus.FOLLOW.arg
)
COMMENT_REACTION_HIDE = Reaction(
    name="Hide comment", id="hide-comment", icon="fa-solid fa-eye-slash",
    aria="Hide comment", type=AJAX,
    url=namespaced_url(OPINIONS_APP_NAME, COMMENT_HIDE_ID_ROUTE_NAME),
    option=ReactionStatus.HIDE.arg
)
COMMENT_REACTION_REPORT = Reaction(
    name="Report comment", id="report-comment",
    icon="fa-solid fa-person-military-pointing",
    aria="Report comment", type=MODAL,
    url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
    option=f"#{COMMENT_MODAL_ID}"
)
COMMENT_REACTIONS_LIST = ReactionsList(
    COMMENT_REACTION_AGREE, COMMENT_REACTION_DISAGREE,
    COMMENT_REACTION_FOLLOW, COMMENT_REACTION_HIDE, COMMENT_REACTION_REPORT)

COMMENT_REACTIONS = [
    COMMENT_REACTION_AGREE,
    COMMENT_REACTION_DISAGREE,
    Reaction(name="Comment", id=f"{COMMENT_REACTION_ID}-comment",
             icon="fa-solid fa-comment",
             aria="Comment on comment", type=MODAL,
             url=namespaced_url(
                 OPINIONS_APP_NAME, COMMENT_COMMENT_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-user-xmark"></i> to unfollow
    COMMENT_REACTION_FOLLOW,
    Reaction(name="Share comment", id="share-comment",
             icon="fa-solid fa-share-nodes",
             aria="Share comment", type=MODAL,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-eye"></i> to un-hide
    COMMENT_REACTION_HIDE,
    COMMENT_REACTION_REPORT,
]


def get_reaction_status(
            user: User, content: [Opinion, Comment, CommentBundle, list],
            statuses: dict = None
        ) -> dict:
    """
    Get the reaction status for the specified content
    :param user: current user
    :param content: opinion/comment/comment bundle or list thereof
    :param statuses: statuses dict to update; default None
    :return: statuses dict
    """
    if statuses is None:
        statuses = {}

    if not isinstance(content, list):
        content = [content]

    for entry in content:
        if isinstance(entry, CommentBundle):
            # get status for bundle comment
            statuses = get_reaction_status(
                user, entry.comment, statuses=statuses)
            # get statuses for replies to bundle comment
            for reply in entry.comments:
                statuses = get_reaction_status(user, reply, statuses=statuses)
        else:
            if isinstance(entry, Opinion):
                field = AgreementStatus.OPINION_FIELD
                reactions_list = OPINION_REACTIONS_LIST
            else:
                field = AgreementStatus.COMMENT_FIELD
                reactions_list = COMMENT_REACTIONS_LIST

            # get agree & disagree statuses for comment/opinion
            agree = False
            disagree = False
            query = AgreementStatus.objects.filter(**{
                AgreementStatus.USER_FIELD: user,
                field: entry
            })
            if query.exists():
                agreement = query.first()
                agree = agreement.status.name == ReactionStatus.AGREE.display
                disagree = \
                    agreement.status.name == ReactionStatus.DISAGREE.display

            # get follow/hidden/report statuses
            following = False
            hidden = False
            reported = False

            statuses.update({
                reaction_button_id(reaction, entry.id):
                    ReactionCtrl(val, entry.user == user)
                    for reaction, val in [
                        (reactions_list.agree, agree),
                        (reactions_list.disagree, disagree),
                        (reactions_list.follow, following),
                        (reactions_list.hide, hidden),
                        (reactions_list.report, reported),
                    ]
            })

    return statuses
