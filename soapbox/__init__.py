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

from .constants import (
    BASE_APP_NAME, USER_APP_NAME, OPINIONS_APP_NAME,
    APP_NAME, COPYRIGHT_YEAR, COPYRIGHT,
    GET, PATCH, POST, DELETE,
    HOME_URL, HOME_ROUTE_NAME,
    ADMIN_URL, ACCOUNTS_URL, SUMMERNOTE_URL,
    USERS_URL, USER_ID_URL, USER_ID_ROUTE_NAME,
    AVATAR_FOLDER, IMAGE_FILE_TYPES
)
from .settings import AVATAR_BLANK_URL, DEVELOPMENT

__all__ = [
    'BASE_APP_NAME',
    'USER_APP_NAME',
    'OPINIONS_APP_NAME',
    'APP_NAME',
    'COPYRIGHT_YEAR',
    'COPYRIGHT',

    'GET',
    'PATCH',
    'POST',
    'DELETE',

    'HOME_URL',
    'HOME_ROUTE_NAME',
    'ADMIN_URL',
    'ACCOUNTS_URL',
    'SUMMERNOTE_URL',
    'USERS_URL',
    'USER_ID_URL',
    'USER_ID_ROUTE_NAME',

    'AVATAR_FOLDER',
    'IMAGE_FILE_TYPES',

    'AVATAR_BLANK_URL',
    'DEVELOPMENT'
]
