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
from utils import append_slash, url_path

# common field names
TITLE_FIELD = "title"
CONTENT_FIELD = "content"
EXCERPT_FIELD = "excerpt"
CATEGORIES_FIELD = 'categories'
STATUS_FIELD = 'status'
USER_FIELD = 'user'
SLUG_FIELD = 'slug'
CREATED_FIELD = 'created'
UPDATED_FIELD = 'updated'
PUBLISHED_FIELD = 'published'

OPINION_FIELD = 'opinion'
REQUESTED_FIELD = 'requested'
REASON_FIELD = 'reason'
REVIEWER_FIELD = 'reviewer'
COMMENT_FIELD = 'comment'
RESOLVED_FIELD = 'resolved'

# Opinion routes related
OPINIONS_URL = ""
OPINION_NEW_URL = append_slash("new")
OPINION_SEARCH_URL = append_slash("search")
OPINION_ID_URL = append_slash("<int:pk>")
OPINION_SLUG_URL = append_slash("<slug:slug>")
OPINION_PREVIEW_ID_URL = url_path("preview", OPINION_ID_URL)
OPINION_STATUS_ID_URL = url_path("status", OPINION_ID_URL)

OPINIONS_ROUTE_NAME = "opinions"
OPINION_NEW_ROUTE_NAME = "opinion_new"
OPINION_SEARCH_ROUTE_NAME = "opinion_search"
OPINION_ID_ROUTE_NAME = "opinion_id"
OPINION_SLUG_ROUTE_NAME = "opinion_slug"
OPINION_PREVIEW_ID_ROUTE_NAME = "preview_opinion_id"
OPINION_STATUS_ID_ROUTE_NAME = "status_opinion_id"

ORDER_QUERY: str = 'order'              # opinion order
PAGE_QUERY: str = 'page'                # page number
PER_PAGE_QUERY: str = 'per-page'        # pagination per page
REORDER_QUERY: str = 'reorder'          # reordering of previous query
SEARCH_QUERY: str = 'search'            # search from search box in header
# Note: a search can have any of the following queries embedded in its
# value
STATUS_QUERY: str = 'status'                # search status
TITLE_QUERY: str = 'title'                  # search title
CONTENT_QUERY: str = 'content'              # search content
CATEGORY_QUERY: str = 'category'            # search category
AUTHOR_QUERY: str = 'author'                # search author
ON_OR_AFTER_QUERY: str = 'after-or-on'      # search >= date
ON_OR_BEFORE_QUERY: str = 'before-or-on'    # search <= date
AFTER_QUERY: str = 'after'                  # search > date
BEFORE_QUERY: str = 'before'                # search < date
EQUAL_QUERY: str = 'date'                   # search == date

OPINION_PAGINATION_ON_EACH_SIDE = 1
OPINION_PAGINATION_ON_ENDS = 1

# permissions related
CLOSE_REVIEW_PERM = "close_review"
WITHDRAW_REVIEW_PERM = "withdraw_review"
