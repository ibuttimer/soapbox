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

from .constants import (
    OPINIONS_URL, OPINIONS_ROUTE_NAME,
    OPINION_NEW_URL, OPINION_NEW_ROUTE_NAME,
    OPINION_ID_URL, OPINION_ID_ROUTE_NAME,
    OPINION_SLUG_URL, OPINION_SLUG_ROUTE_NAME,
    OPINION_PREVIEW_ID_URL, OPINION_PREVIEW_ID_ROUTE_NAME,
    OPINION_STATUS_ID_URL, OPINION_STATUS_ID_ROUTE_NAME
)
from .views_create import OpinionCreate
from .views_by_id import (
    OpinionDetailById, OpinionDetailBySlug, OpinionDetailPreviewById,
    opinion_status_patch
)
from .views_list import OpinionList


urlpatterns = [
    path(OPINIONS_URL, OpinionList.as_view(),
         name=OPINIONS_ROUTE_NAME),
    path(OPINION_NEW_URL, OpinionCreate.as_view(),
         name=OPINION_NEW_ROUTE_NAME),
    path(OPINION_ID_URL, OpinionDetailById.as_view(),
         name=OPINION_ID_ROUTE_NAME),
    path(OPINION_SLUG_URL, OpinionDetailBySlug.as_view(),
         name=OPINION_SLUG_ROUTE_NAME),
    path(OPINION_PREVIEW_ID_URL, OpinionDetailPreviewById.as_view(),
         name=OPINION_PREVIEW_ID_ROUTE_NAME),
    path(OPINION_STATUS_ID_URL, opinion_status_patch,
         name=OPINION_STATUS_ID_ROUTE_NAME),
]
