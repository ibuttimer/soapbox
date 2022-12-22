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

from utils import append_slash, url_path

APP_NAME = "SoapBox"
COPYRIGHT_YEAR = 2022
COPYRIGHT = "Ian Buttimer"

# Namespace related
BASE_APP_NAME = "base"
USER_APP_NAME = "user"
CATEGORIES_APP_NAME = "categories"
OPINIONS_APP_NAME = "opinions"

# Request methods
GET = 'GET'
PATCH = 'PATCH'
POST = 'POST'
DELETE = 'DELETE'

# Base routes related
HOME_URL = "/"
HELP_URL = append_slash("help")
FEED_URL = append_slash("feed")

HOME_ROUTE_NAME = "home"
HELP_ROUTE_NAME = "help"
LANDING_ROUTE_NAME = "landing"

HOME_MENU_CTX = "home_menu"
OPINION_MENU_CTX = "opinion_menu"
COMMENT_MENU_CTX = "comment_menu"
MODERATOR_MENU_CTX = "moderator_menu"
USER_MENU_CTX = "user_menu"
SIGN_IN_MENU_CTX = "sign_in_menu"
REGISTER_MENU_CTX = "register_menu"
HELP_MENU_CTX = "help_menu"

IS_SUPER_CTX = "is_super"
IS_MODERATOR_CTX = "is_moderator"
IS_AUTHOR_CTX = "is_author"
IS_DEVELOPMENT_CTX = "is_development"
IS_TEST_CTX = "is_test"


# Admin routes related
ADMIN_URL = append_slash("admin")

# Accounts routes related
ACCOUNTS_URL = append_slash("accounts")

# mounting allauth on 'accounts' and copying paths from
# allauth/account/urls.py
LOGIN_URL = url_path(ACCOUNTS_URL, "login")
REGISTER_URL = url_path(ACCOUNTS_URL, "signup")
# copying route names from allauth/account/urls.py
LOGIN_ROUTE_NAME = "account_login"
REGISTER_ROUTE_NAME = "account_signup"

# Summernote routes related
SUMMERNOTE_URL = append_slash("summernote")

# User routes related
USERS_URL = append_slash("users")

# Opinion routes related
OPINIONS_URL = append_slash("opinions")

# CSS/HTML validator test related
VAL_TEST_PATH_PREFIX = 'val-test'

# cloudinary related
AVATAR_FOLDER = "soapbox"

# https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types#common_image_file_types
# Pillow which is used by ImageField in dev mode doesn't support avif or svg
DEV_IMAGE_FILE_TYPES = [
    "image/apng", "image/gif", "image/jpeg", "image/png", "image/webp"
]
IMAGE_FILE_TYPES = DEV_IMAGE_FILE_TYPES.copy()
IMAGE_FILE_TYPES.extend([
    "image/avif", "image/svg+xml"
])

MIN_PASSWORD_LEN = 8
