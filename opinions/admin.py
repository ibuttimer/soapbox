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
from django.contrib import admin

from .models import Opinion, Comment, Review, AgreementStatus, HideStatus


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    """ Class representing the Opinion model in the admin interface """
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """ Class representing the Comment model in the admin interface """
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """ Class representing the Review model in the admin interface """
    pass


@admin.register(AgreementStatus)
class AgreementStatusAdmin(admin.ModelAdmin):
    """
    Class representing the AgreementStatus model in the admin interface
    """
    pass


@admin.register(HideStatus)
class HideStatusAdmin(admin.ModelAdmin):
    """ Class representing the HideStatus model in the admin interface """
    pass
