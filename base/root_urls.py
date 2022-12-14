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

from soapbox import val_test_route_name
from soapbox.constants import (
    LANDING_ROUTE_NAME, HOME_ROUTE_NAME, VAL_TEST_PATH_PREFIX, HELP_URL,
    HELP_ROUTE_NAME
)
from .views import get_landing, get_help

urlpatterns = [
    # TODO duplicate routes
    # val-test urls
    path(VAL_TEST_PATH_PREFIX, get_landing,
         name=val_test_route_name(HOME_ROUTE_NAME)),
    path(VAL_TEST_PATH_PREFIX, get_landing,
         name=val_test_route_name(LANDING_ROUTE_NAME)),

    # standard app urls
    path(HELP_URL, get_help, name=HELP_ROUTE_NAME),
    path('', get_landing, name=HOME_ROUTE_NAME),
    path('', get_landing, name=LANDING_ROUTE_NAME),
]
