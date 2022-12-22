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
from django.forms import CharField, Textarea, ChoiceField, RadioSelect
from django.utils.translation import gettext_lazy as _

from django import forms
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget

from utils import update_field_widgets, error_messages, ErrorMsgs
from .constants import (
    TITLE_FIELD, CONTENT_FIELD, CATEGORIES_FIELD, STATUS_FIELD, SLUG_FIELD,
    CREATED_FIELD, UPDATED_FIELD, PUBLISHED_FIELD, REASON_FIELD, OPINION_FIELD,
    REQUESTED_FIELD, REVIEWER_FIELD, COMMENT_FIELD, RESOLVED_FIELD,
    REVIEW_RESULT_FIELD
)
from .enums import QueryStatus
from .models import Opinion, Category, Comment, Review


class OpinionForm(forms.ModelForm):
    """
    Form to create/update an opinion.
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

    content = SummernoteTextField(
        max_length=Opinion.OPINION_ATTRIB_CONTENT_MAX_LEN,
        blank=False)

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
            model.model_name_caps(),
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
             if field not in OpinionForm.Meta.non_bootstrap_fields
             and field != CATEGORIES_FIELD],
            {'class': 'form-control'})
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [CATEGORIES_FIELD],
            {'class': 'form-select'})


class CommentForm(forms.ModelForm):
    """
    Form to create/update a comment.
    """

    CONTENT_FF = CONTENT_FIELD
    STATUS_FF = STATUS_FIELD
    SLUG_FF = SLUG_FIELD
    CREATED_FF = CREATED_FIELD
    UPDATED_FF = UPDATED_FIELD
    PUBLISHED_FF = PUBLISHED_FIELD

    content = SummernoteTextField(
        max_length=Comment.COMMENT_ATTRIB_CONTENT_MAX_LEN,
        blank=False)

    class Meta:
        model = Comment
        fields = [
            CONTENT_FIELD
        ]
        non_bootstrap_fields = [CONTENT_FIELD]
        help_texts = {
            CONTENT_FIELD: 'Comment content.',
        }
        error_messages = error_messages(
            model.model_name_caps(),
            *[ErrorMsgs(field, max_length=True)
              for field in (CONTENT_FIELD, )]
        )
        widgets = {
            CONTENT_FIELD: SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        # [groupName, [list of button]]
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['font',
                            ['strikethrough', 'superscript', 'subscript']],
                        ['fontsize', ['fontsize']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['height', ['height']],
                    ],
                    'height': '240',
                }
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in CommentForm.Meta.fields
             if field not in CommentForm.Meta.non_bootstrap_fields],
            {'class': 'form-control'})


class ReportForm(forms.ModelForm):
    """
    Form to create a content report.
    """

    OPINION_FF = OPINION_FIELD
    COMMENT_FF = COMMENT_FIELD
    REQUESTED_FF = REQUESTED_FIELD
    REASON_FF = REASON_FIELD
    REVIEWER_FF = REVIEWER_FIELD
    STATUS_FF = STATUS_FIELD
    CREATED_FF = CREATED_FIELD
    UPDATED_FF = UPDATED_FIELD
    RESOLVED_FF = RESOLVED_FIELD

    reason = CharField(
        max_length=Review.REVIEW_ATTRIB_REASON_MAX_LEN,
        widget=Textarea(attrs={
            "maxlength": Review.REVIEW_ATTRIB_REASON_MAX_LEN,
            "cols": "40",
            "rows": "5",
            "placeholder": _("Reason details")
        }))

    class Meta:
        model = Review
        fields = [
            REASON_FIELD
        ]
        non_bootstrap_fields = []
        help_texts = {
            REASON_FIELD: 'Reason content.',
        }
        error_messages = error_messages(
            model.model_name_caps(),
            *[ErrorMsgs(field, max_length=True)
              for field in (REASON_FIELD, )]
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in ReportForm.Meta.fields
             if field not in ReportForm.Meta.non_bootstrap_fields],
            {'class': 'form-control'})


class ReviewForm(ReportForm):
    """
    Form to create a content review.
    """

    REVIEW_RESULT_FF = REVIEW_RESULT_FIELD

    review_result = ChoiceField(
        choices=[
            (choice.arg, choice.display)
            for choice in QueryStatus.review_result_statuses()
        ],
        label="Review Decision",
        widget=RadioSelect()
    )

    class Meta:
        model = Review
        fields = [
            REASON_FIELD, REVIEW_RESULT_FIELD
        ]
        non_bootstrap_fields = []
        help_texts = {
            REASON_FIELD: 'Reason content.',
            STATUS_FIELD: 'Review decision.',
        }
        error_messages = error_messages(
            model.model_name_caps(),
            *[ErrorMsgs(field, max_length=True)
              for field in (REASON_FIELD, )]
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in ReviewForm.Meta.fields
             if field not in ReviewForm.Meta.non_bootstrap_fields],
            {'class': 'form-control'})
