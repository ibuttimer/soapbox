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

from django.utils.translation import gettext_lazy as _

from django import forms
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget

from utils import update_field_widgets, error_messages, ErrorMsgs
from .constants import (
    TITLE_FIELD, CONTENT_FIELD, CATEGORIES_FIELD, STATUS_FIELD, SLUG_FIELD,
    CREATED_FIELD, UPDATED_FIELD, PUBLISHED_FIELD
)
from .models import Opinion, Category, Status


class OpinionForm(forms.ModelForm):
    """
    Form to update a user.
    """

    TITLE_FF = TITLE_FIELD
    CONTENT_FF = CONTENT_FIELD
    CATEGORIES_FF = CATEGORIES_FIELD
    STATUS_FF = STATUS_FIELD
    SLUG_FF = SLUG_FIELD
    CREATED_FF = CREATED_FIELD
    UPDATED_FF = UPDATED_FIELD
    PUBLISHED_FF = PUBLISHED_FIELD

    title = forms.CharField(
        label=_("Title"),
        max_length=Opinion.OPINION_ATTRIB_TITLE_MAX_LEN,
        required=True)

    content = SummernoteTextField(blank=False)

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), required=True
    )

    class Meta:
        model = Opinion
        fields = [
            TITLE_FIELD, CONTENT_FIELD, CATEGORIES_FIELD
        ]
        non_bootstrap_fields = [CONTENT_FIELD]
        help_texts = {
            TITLE_FIELD: 'Opinion title.',
            CONTENT_FIELD: 'Opinion content.',
            CATEGORIES_FIELD: 'Opinion categories.',
        }
        error_messages = error_messages(
            model.MODEL_NAME,
            *[ErrorMsgs(field, max_length=True)
              for field in (TITLE_FIELD, CONTENT_FIELD)]
        )
        widgets = {
            CONTENT_FIELD: SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in OpinionForm.Meta.fields
             if field not in OpinionForm.Meta.non_bootstrap_fields],
            {'class': 'form-control'})
