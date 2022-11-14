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
from .misc import (
    append_slash, namespaced_url, app_template_path, url_path, reverse_q,
    random_string_generator, is_boolean_true, Crud, permission_name,
    permission_check
)
from .views import redirect_on_success_or_render
from .forms import update_field_widgets, error_messages, ErrorMsgs
from .file import find_parent_of_folder
from .models import (
    SlugMixin, ModelMixin, DESC_LOOKUP, DATE_OLDEST_LOOKUP, DATE_NEWEST_LOOKUP
)


__all__ = [
    'append_slash',
    'namespaced_url',
    'app_template_path',
    'url_path',
    'reverse_q',
    'random_string_generator',
    'is_boolean_true',
    'Crud',
    'permission_name',
    'permission_check',

    'redirect_on_success_or_render',

    'update_field_widgets',
    'error_messages',
    'ErrorMsgs',

    'find_parent_of_folder',

    'SlugMixin',
    'ModelMixin',
    'DESC_LOOKUP',
    'DATE_OLDEST_LOOKUP',
    'DATE_NEWEST_LOOKUP'
]
