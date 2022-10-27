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

from django.urls import path

from soapbox import OPINIONS_APP_NAME

from .constants import (
    OPINIONS_URL, OPINIONS_ROUTE_NAME,
    OPINION_NEW_URL, OPINION_NEW_ROUTE_NAME,
    OPINION_SEARCH_URL, OPINION_SEARCH_ROUTE_NAME,
    OPINION_ID_URL, OPINION_ID_ROUTE_NAME,
    OPINION_SLUG_URL, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_URL, OPINION_PREVIEW_ID_ROUTE_NAME,
    OPINION_STATUS_ID_URL, OPINION_STATUS_ID_ROUTE_NAME,
    OPINION_LIKE_ID_URL, OPINION_LIKE_ID_ROUTE_NAME,
    OPINION_HIDE_ID_URL, OPINION_HIDE_ID_ROUTE_NAME,
    OPINION_PIN_ID_URL, OPINION_PIN_ID_ROUTE_NAME,
    OPINION_REPORT_ID_URL, OPINION_REPORT_ID_ROUTE_NAME,
    OPINION_COMMENT_ID_URL, OPINION_COMMENT_ID_ROUTE_NAME,
    COMMENTS_URL, COMMENTS_ROUTE_NAME,
    COMMENT_ID_URL, COMMENT_ID_ROUTE_NAME,
    COMMENT_LIKE_ID_URL, COMMENT_LIKE_ID_ROUTE_NAME,
    COMMENT_COMMENT_ID_URL, COMMENT_COMMENT_ID_ROUTE_NAME, COMMENT_SEARCH_URL,
    COMMENT_SEARCH_ROUTE_NAME, COMMENT_MORE_URL, COMMENT_MORE_ROUTE_NAME,
    COMMENT_HIDE_ID_URL, COMMENT_HIDE_ID_ROUTE_NAME,
    COMMENT_REPORT_ID_URL, COMMENT_REPORT_ID_ROUTE_NAME,
)
from .views_comment_create import OpinionCommentCreate, CommentCommentCreate
from .views_comment_list import CommentList, CommentSearch, opinion_comments
from .views_opinion_create import OpinionCreate
from .views_opinion_by_id import (
    OpinionDetailById, OpinionDetailBySlug, OpinionDetailPreviewById,
    opinion_status_patch, opinion_like_patch, opinion_hide_patch,
    opinion_pin_patch, opinion_report_post
)
from .views_opinion_list import OpinionList, OpinionSearch


# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = OPINIONS_APP_NAME

urlpatterns = [
    # list opinions
    path(OPINIONS_URL, OpinionList.as_view(), name=OPINIONS_ROUTE_NAME),
    # search opinions
    path(OPINION_SEARCH_URL, OpinionSearch.as_view(),
         name=OPINION_SEARCH_ROUTE_NAME),
    # create opinion
    path(OPINION_NEW_URL, OpinionCreate.as_view(),
         name=OPINION_NEW_ROUTE_NAME),
    # get/update opinion by id
    path(OPINION_ID_URL, OpinionDetailById.as_view(),
         name=OPINION_ID_ROUTE_NAME),
    # preview opinion by id
    path(OPINION_PREVIEW_ID_URL, OpinionDetailPreviewById.as_view(),
         name=OPINION_PREVIEW_ID_ROUTE_NAME),
    # patch opinion status by id
    path(OPINION_STATUS_ID_URL, opinion_status_patch,
         name=OPINION_STATUS_ID_ROUTE_NAME),
    # patch opinion like/unlike status by id
    path(OPINION_LIKE_ID_URL, opinion_like_patch,
         name=OPINION_LIKE_ID_ROUTE_NAME),
    # patch opinion hide status by id
    path(OPINION_HIDE_ID_URL, opinion_hide_patch,
         name=OPINION_HIDE_ID_ROUTE_NAME),
    # patch opinion pin status by id
    path(OPINION_PIN_ID_URL, opinion_pin_patch,
         name=OPINION_PIN_ID_ROUTE_NAME),
    # post opinion report by id
    path(OPINION_REPORT_ID_URL, opinion_report_post,
         name=OPINION_REPORT_ID_ROUTE_NAME),

    # create comment for opinion by id
    path(OPINION_COMMENT_ID_URL, OpinionCommentCreate.as_view(),
         name=OPINION_COMMENT_ID_ROUTE_NAME),

    # list comments
    path(COMMENTS_URL, CommentList.as_view(),
         name=COMMENTS_ROUTE_NAME),

    # FIXME comment id/like/hide/report urls
    path(COMMENT_ID_URL, opinion_status_patch,
         name=COMMENT_ID_ROUTE_NAME),

    path(COMMENT_LIKE_ID_URL, opinion_like_patch,
         name=COMMENT_LIKE_ID_ROUTE_NAME),
    path(COMMENT_HIDE_ID_URL, opinion_hide_patch,
         name=COMMENT_HIDE_ID_ROUTE_NAME),


    path(COMMENT_REPORT_ID_URL, opinion_hide_patch,
         name=COMMENT_REPORT_ID_ROUTE_NAME),

    # search comments
    path(COMMENT_SEARCH_URL, CommentSearch.as_view(),
         name=COMMENT_SEARCH_ROUTE_NAME),
    # more comments
    path(COMMENT_MORE_URL, opinion_comments,
         name=COMMENT_MORE_ROUTE_NAME),

    # create comment for comment by id
    path(COMMENT_COMMENT_ID_URL, CommentCommentCreate.as_view(),
         name=COMMENT_COMMENT_ID_ROUTE_NAME),

    # TODO slug has be last as it'll match the 'comment' url. Move comments
    # to own app?

    # get/update opinion by slug
    path(OPINION_SLUG_URL, OpinionDetailBySlug.as_view(),
         name=OPINION_SLUG_ROUTE_NAME),

]
