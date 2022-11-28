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
from typing import Union, Any

from django import template

register = template.Library()

# https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/#simple-tags


@register.simple_tag
def calc(
    a: Union[int, str, list, tuple], op: str, b: Union[int, str, list, tuple]
) -> Union[int, float]:
    """
    Perform simple calculations. If an operation is a list or tuple, its
    length is used in the calculation.
    :param a: first operand
    :param op: operation; '/', '*' etc.
    :param b: second operand
    :return: int/float result
    """
    a = _convert(a)
    b = _convert(b)
    result = eval(f'{a}{op}{b}')
    return int(result) if result == int(result) else result


def _convert(a: Union[int, str, list, tuple]) -> Any:
    """ Convert operand """
    if isinstance(a, list) or isinstance(a, tuple):
        a = len(a)
    elif isinstance(a, str):
        if a.isdecimal():
            a = int(a)
        elif a.isnumeric():
            a = float(a)
    return a
