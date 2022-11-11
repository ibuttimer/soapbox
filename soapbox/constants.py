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

HOME_ROUTE_NAME = "home"

# Admin routes related
ADMIN_URL = append_slash("admin")

# Accounts routes related
ACCOUNTS_URL = append_slash("accounts")
LOGIN_URL = url_path(ACCOUNTS_URL, "login")

# Summernote routes related
SUMMERNOTE_URL = append_slash("summernote")

# User routes related
USERS_URL = append_slash("users")

# Opinion routes related
OPINIONS_URL = append_slash("opinions")

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
