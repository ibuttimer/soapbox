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
from utils import namespaced_url
from .constants import (
    OPINION_ID_ROUTE_NAME, OPINION_LIKE_ID_ROUTE_NAME,
    OPINION_COMMENT_ID_ROUTE_NAME, COMMENT_LIKE_ID_ROUTE_NAME,
    COMMENT_COMMENT_ID_ROUTE_NAME
)

MODAL = "modal"
AJAX = "ajax"
Reaction = namedtuple("Reaction", [
    "name",         # reaction name
    "id",           # identifier, used to generate ids for reaction buttons
    "icon",         # icon to use
    "aria",         # aria label
    "type",         # type; 'modal' or 'ajax'
    "url",          # url for ajax
    "option",       # selected option/target modal
    "disabled",     # reaction disabled
], defaults=['', '', '', '', '', '', '', False])

COMMENT_MODAL_ID = 'id--comment-modal'
COMMENT_REACTION_ID = 'comment'     # used to id comment modal button in js

# TODO share/hide/report

OPINION_REACTIONS = [
    Reaction(name="Agree", id="agree-opinion",
             icon="fa-solid fa-hands-clapping",
             aria="Agree with opinion", type=AJAX,
             url=namespaced_url(
                 OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Disagree", id="disagree-opinion",
             icon="fa-solid fa-thumbs-down",
             aria="Disagree with opinion", type=AJAX,
             url=namespaced_url(
                 OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Comment", id=f"{COMMENT_REACTION_ID}-opinion",
             icon="fa-solid fa-comment",
             aria="Comment on opinion", type=MODAL,
             url=namespaced_url(
                 OPINIONS_APP_NAME, OPINION_COMMENT_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-user-xmark"></i> to unfollow
    Reaction(name="Follow author", id="follow-opinion",
             icon="fa-solid fa-user-tag",
             aria="Follow opinion author", type=AJAX,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Share opinion", id="share-opinion",
             icon="fa-solid fa-share-nodes",
             aria="Share opinion", type=MODAL,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-eye"></i> to un-hide
    Reaction(name="Hide opinion", id="hide-opinion",
             icon="fa-solid fa-eye-slash",
             aria="Hide opinion", type=AJAX,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Report opinion", id="report-opinion",
             icon="fa-solid fa-person-military-pointing",
             aria="Report opinion", type=MODAL,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
]

COMMENT_REACTIONS = [
    Reaction(name="Agree", id="agree-comment",
             icon="fa-solid fa-hands-clapping",
             aria="Agree with comment", type=AJAX,
             url=namespaced_url(
                 OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Disagree", id="disagree-comment",
             icon="fa-solid fa-thumbs-down",
             aria="Disagree with comment", type=AJAX,
             url=namespaced_url(
                 OPINIONS_APP_NAME, COMMENT_LIKE_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Comment", id=f"{COMMENT_REACTION_ID}-comment",
             icon="fa-solid fa-comment",
             aria="Comment on comment", type=MODAL,
             url=namespaced_url(
                 OPINIONS_APP_NAME, COMMENT_COMMENT_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-user-xmark"></i> to unfollow
    Reaction(name="Follow author", id="follow-comment",
             icon="fa-solid fa-user-tag",
             aria="Follow comment author", type=AJAX,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Share comment", id="share-comment",
             icon="fa-solid fa-share-nodes",
             aria="Share comment", type=MODAL,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
    # TODO <i class="fa-solid fa-eye"></i> to un-hide
    Reaction(name="Hide comment", id="hide-comment",
             icon="fa-solid fa-eye-slash",
             aria="Hide comment", type=AJAX,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=""),
    Reaction(name="Report comment", id="report-comment",
             icon="fa-solid fa-person-military-pointing",
             aria="Report comment", type=MODAL,
             url=namespaced_url(OPINIONS_APP_NAME, OPINION_ID_ROUTE_NAME),
             option=f"#{COMMENT_MODAL_ID}"),
]
