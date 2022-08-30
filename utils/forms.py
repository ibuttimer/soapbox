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

from collections import namedtuple
from string import Template
from typing import Type, Union, NoReturn

from django.forms import BaseForm
from django.utils.translation import gettext_lazy as _


ALL_FIELDS = "__all__"


_ATTRIB = 'attrib'
_MAX_LEN = 'max_length'
_MIN_LEN = 'min_length'

ErrorMsgs: Type[tuple] = namedtuple(
    'ErrorMsgs',
    [_ATTRIB, _MAX_LEN, _MIN_LEN],
    defaults=['', False, False]
)

_msg_templates = {
    _MAX_LEN: Template(f'The ${_ATTRIB} is too long.'),
    _MIN_LEN: Template(f'The ${_ATTRIB} is too short.')
}


def error_messages(model: str, *args: ErrorMsgs) -> dict:
    """
    Generate help texts for the specified attributes of 'model'.
    Note: currently only supports min/max length.
    :param model:   name of model
    :param args:    list of attributes
    :return: dict of help texts of the form 'Model attrib.'
    """
    def inc_msg(fld: str, err_msg: ErrorMsgs):
        # Check if field is not attrib & value is true
        return fld != _ATTRIB and getattr(err_msg, fld)

    messages = {}
    for entry in args:
        messages[entry.attrib] = dict(
            zip(
                [k for k in ErrorMsgs._fields if inc_msg(k, entry)],
                [_msg_templates[k].substitute({_ATTRIB: entry.attrib})
                 for k in ErrorMsgs._fields if inc_msg(k, entry)]
            )
        )
    return messages


def update_field_widgets(form: BaseForm,
                         fields: Union[list[str], tuple[str], str],
                         attrs_update: dict) -> NoReturn:
    """
    Update the widget attributes for the specified fields in 'form'.
    :param form:        django form
    :param fields:      list of names of fields to update, or use '__all__' to
                        update all fields
    :param attrs_update:    updates to apply to widgets
    """
    fld_names: list
    if fields == ALL_FIELDS:
        fld_names = form.fields.keys()
    else:
        fld_names = fields
    for name in fld_names:
        form.fields[name].widget.attrs.update(attrs_update)
