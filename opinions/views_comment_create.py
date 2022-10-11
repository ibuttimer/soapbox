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
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest, HttpResponse, JsonResponse
)
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from categories import STATUS_PUBLISHED
from categories.models import Status
from soapbox import (
    OPINIONS_APP_NAME
)
from utils import (
    Crud, app_template_path
)
from .comment_data import CommentBundle
from .forms import CommentForm
from .models import Opinion, Comment
from .reactions import COMMENT_REACTIONS
from .views_utils import (
    comment_permission_check, timestamp_content
)


class CommentCreate(LoginRequiredMixin, View):
    """
    Class-based view for comment creation
    """
    # https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequired-mixin

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to create Comment
        :param request: http request
        :param pk:      id of opinion/comment
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        comment_permission_check(request, Crud.CREATE)

        form = CommentForm(data=request.POST)

        if form.is_valid():
            # save new object
            form.instance.user = request.user
            self.comment_hierarchy(form.instance, pk)
            form.instance.status = Status.objects.get(name=STATUS_PUBLISHED)
            form.instance.set_slug(form.instance.content)

            timestamp_content(form.instance)

            comment = form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            # container for new comment display is the collapse
            # container of the parent comment if comment-on-comment
            # else comments container for comment-on-opinion
            parent_container = \
                CommentBundle.generate_collapse_id(comment.parent) \
                if comment.parent != Comment.NO_PARENT else \
                "id--comments-container"

            response = JsonResponse({
                'html': render_to_string(
                    app_template_path(
                        OPINIONS_APP_NAME, "snippet", "comment_bundle.html"),
                    context={
                        'bundle': CommentBundle(comment),
                        'target_id': comment.id,
                        'comment_reactions': COMMENT_REACTIONS,
                    },
                    request=request),
                'parent_container': parent_container,
                'opinion_comment': comment.parent == Comment.NO_PARENT,
            }, status=HTTPStatus.OK)
        else:
            # display form errors
            response = JsonResponse({
                'html': render_to_string(
                    app_template_path(
                        "snippet", "form_errors.html"),
                    context={
                        'form': form,
                    },
                    request=request),
            }, status=HTTPStatus.BAD_REQUEST)

        return response

    def comment_hierarchy(self, comment: Comment, pk: int):
        """
        Set the comment hierarchy fields
        :param comment: comment instance
        :param pk:      id of opinion/comment
        :return:
        """
        raise NotImplementedError(
            "'comment_hierarchy' method must be overridden by sub classes")


class OpinionCommentCreate(CommentCreate):
    """
    Class-based view for opinion comment creation
    """
    # https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequired-mixin

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to create Comment
        :param request: http request
        :param pk:      id of opinion
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super(OpinionCommentCreate, self).post(request, pk)

    def comment_hierarchy(self, comment: Comment, pk: int):
        """
        Set the comment hierarchy fields
        :param comment: comment instance
        :param pk:      id of opinion/comment
        """
        comment.opinion = get_object_or_404(Opinion, pk=pk)
        comment.level = 0
        comment.parent = Comment.NO_PARENT


class CommentCommentCreate(CommentCreate):
    """
    Class-based view for comment on comment creation
    """
    # https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequired-mixin

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to create Comment
        :param request: http request
        :param pk:      id of opinion
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        return super(CommentCommentCreate, self).post(request, pk)

    def comment_hierarchy(self, comment: Comment, pk: int):
        """
        Set the comment hierarchy fields
        :param comment: comment instance
        :param pk:      id of opinion/comment
        """
        parent = get_object_or_404(Comment, pk=pk)
        comment.opinion = parent.opinion
        comment.level = parent.level + 1
        comment.parent = parent.id
