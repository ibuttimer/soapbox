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

from soapbox import USER_APP_NAME, val_test_url, val_test_route_name

from .constants import (
    USER_ID_URL, USER_ID_ROUTE_NAME, USER_USERNAME_URL,
    USER_USERNAME_ROUTE_NAME
)
from . import views


# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = USER_APP_NAME

urlpatterns = [
    # val-test urls
    path(val_test_url(USER_USERNAME_URL),
         views.UserDetailByUsername.as_view(),
         name=val_test_route_name(USER_USERNAME_ROUTE_NAME)),

    # standard app urls
    path(USER_ID_URL, views.UserDetailById.as_view(), name=USER_ID_ROUTE_NAME),
    path(USER_USERNAME_URL, views.UserDetailByUsername.as_view(),
         name=USER_USERNAME_ROUTE_NAME),
]
