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
from datetime import datetime
from base64 import urlsafe_b64encode
from django.db.models import Model
from django.utils.text import slugify
from .misc import random_string_generator


class SlugMixin:
    """
    A mixin to support slugs
    """

    MIN_RANDOM_LEN = 3
    MAX_ATTEMPTS = 20

    @staticmethod
    def generate_slug(max_len: int, title: str,
                      random_size: int = MIN_RANDOM_LEN):
        """
        Generate a slug in the form of
        `title-abc-<base64 encoded timestamp><random string>`, assuming
        `model` has a CharField called slug.
        :param max_len: max length of slug
        :param title: text to base slug on
        :param random_size: length of random string
        :return:
        """
        if random_size < SlugMixin.MIN_RANDOM_LEN:
            random_size = SlugMixin.MIN_RANDOM_LEN

        # slug should contain only letters, numbers, underscores or hyphens
        slug = slugify(title)

        # Base64 alphabet contains 'a-z', 'A-Z', '0-9', '+', '/', '='
        # urlsafe_b64encode output contains 'a-z', 'A-Z', '0-9', '-', '_', '='
        # so only problem using base64 for slug is padding '=' so replace
        # with '_'
        random_str = '-' + str(
            urlsafe_b64encode(
                bytes(f'{datetime.now().timestamp()}',
                      encoding='utf-8')),
            encoding='utf-8'
        ).replace('=', '_') + random_string_generator(random_size)

        if len(random_str) > max_len:
            raise ValueError(
                f'Slug random string length exceeds max allowed {max_len}')

        slugified = slug if len(slug) < max_len - len(random_str)\
            else slug[:max_len - len(random_str)]
        slugified += random_str

        return slugified

    @staticmethod
    def generate_unique_slug(model: Model, max_len: int, title: str,
                             max_random_len: int = 6):
        """
        Generate a slug in the form of
        `title-abc-<base64 encoded timestamp><random string>`, assuming
        `model` has a CharField called slug.
        :param model: model to generate slug for
        :param max_len: max length of slug
        :param title: text to base slug on
        :param max_random_len: max length of random string, default 6
        :return:
        """
        if max_random_len < SlugMixin.MIN_RANDOM_LEN:
            max_random_len = SlugMixin.MIN_RANDOM_LEN + 1

        # slug should contain only letters, numbers, underscores or hyphens
        slug = slugify(title)

        for random_size in \
                range(SlugMixin.MIN_RANDOM_LEN, max_random_len):
            for attempt in range(SlugMixin.MAX_ATTEMPTS):
                slugified = SlugMixin.generate_slug(
                    max_len, title, random_size)

                if not model.__class__.objects.filter(slug=slug).exists():
                    break
            else:
                slugified = None

            if slugified:
                break
        else:
            raise ValueError(
                f"Unable to generate slug for '{title}', {max_random_len}")

        return slugified
