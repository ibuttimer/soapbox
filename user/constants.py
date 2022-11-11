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
from utils import append_slash

# common field names
FIRST_NAME = "first_name"
LAST_NAME = "last_name"
EMAIL = "email"
USERNAME = "username"
PASSWORD = "password1"
PASSWORD_CONFIRM = "password2"
BIO = "bio"
AVATAR = "avatar"
CATEGORIES = 'categories'
GROUPS = 'groups'
PREVIOUS_LOGIN = 'previous_login'

AUTHOR_GROUP = 'Author'
MODERATOR_GROUP = 'Moderator'

# User routes related
USER_ID_URL = append_slash("<int:pk>")
USER_USERNAME_URL = append_slash("<str:pk>")

USER_ID_ROUTE_NAME = "user_id"
USER_USERNAME_ROUTE_NAME = "user_id"
