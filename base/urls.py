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

"""soapbox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from opinions.views.opinion_list import (
    OpinionCategoryFeed, OpinionFollowedFeed, OpinionAllFeed
)
from soapbox import BASE_APP_NAME, val_test_url, val_test_route_name
from .constants import (
    FOLLOWING_FEED_URL, FOLLOWING_FEED_ROUTE_NAME,
    CATEGORY_FEED_URL, CATEGORY_FEED_ROUTE_NAME, ALL_FEED_URL,
    ALL_FEED_ROUTE_NAME,
)

app_name = BASE_APP_NAME

urlpatterns = [
    # val-test urls
    path(val_test_url(FOLLOWING_FEED_URL), OpinionFollowedFeed.as_view(),
         name=val_test_route_name(FOLLOWING_FEED_ROUTE_NAME)),
    path(val_test_url(CATEGORY_FEED_URL), OpinionCategoryFeed.as_view(),
         name=val_test_route_name(CATEGORY_FEED_ROUTE_NAME)),

    # standard app urls
    path(FOLLOWING_FEED_URL, OpinionFollowedFeed.as_view(),
         name=FOLLOWING_FEED_ROUTE_NAME),
    path(CATEGORY_FEED_URL, OpinionCategoryFeed.as_view(),
         name=CATEGORY_FEED_ROUTE_NAME),
    path(ALL_FEED_URL, OpinionAllFeed.as_view(),
         name=ALL_FEED_ROUTE_NAME),
]
