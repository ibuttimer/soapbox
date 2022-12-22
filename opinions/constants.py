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
ID_FIELD = "id"
TITLE_FIELD = "title"
CONTENT_FIELD = "content"
EXCERPT_FIELD = "excerpt"
CATEGORIES_FIELD = 'categories'
STATUS_FIELD = 'status'
IS_CURRENT_FIELD = 'is_current'
USER_FIELD = 'user'
SLUG_FIELD = 'slug'
CREATED_FIELD = 'created'
UPDATED_FIELD = 'updated'
PUBLISHED_FIELD = 'published'
PARENT_FIELD = 'parent'
LEVEL_FIELD = 'level'

OPINION_FIELD = 'opinion'
REQUESTED_FIELD = 'requested'
REASON_FIELD = 'reason'
REVIEWER_FIELD = 'reviewer'
COMMENT_FIELD = 'comment'
RESOLVED_FIELD = 'resolved'
AUTHOR_FIELD = 'author'
REVIEW_RESULT_FIELD = 'review_result'

# Opinion routes related
PK_PARAM_NAME = "pk"
SLUG_PARAM_NAME = "slug"
OPINIONS_URL = ""
OPINION_NEW_URL = append_slash("new")
OPINION_SEARCH_URL = append_slash("search")
OPINION_FOLLOWED_URL = append_slash("followed")
OPINION_IN_REVIEW_URL = append_slash("in_review")
OPINION_ID_URL = append_slash(f"<int:{PK_PARAM_NAME}>")
OPINION_SLUG_URL = append_slash(f"<slug:{SLUG_PARAM_NAME}>")
OPINION_PREVIEW_ID_URL = url_path(OPINION_ID_URL, "preview")
OPINION_STATUS_ID_URL = url_path(OPINION_ID_URL, "status")
OPINION_LIKE_ID_URL = url_path(OPINION_ID_URL, "like")
OPINION_HIDE_ID_URL = url_path(OPINION_ID_URL, "hide")
OPINION_PIN_ID_URL = url_path(OPINION_ID_URL, "pin")
OPINION_REPORT_ID_URL = url_path(OPINION_ID_URL, "report")
OPINION_COMMENT_ID_URL = url_path(OPINION_ID_URL, "comment")
OPINION_FOLLOW_ID_URL = url_path(OPINION_ID_URL, "follow")
OPINION_REVIEW_STATUS_ID_URL = url_path(OPINION_ID_URL, "review_status")
OPINION_REVIEW_DECISION_ID_URL = url_path(OPINION_ID_URL, "review_decision")

COMMENTS_URL = append_slash("comments")
COMMENT_SEARCH_URL = url_path(COMMENTS_URL, "search")
COMMENT_MORE_URL = url_path(COMMENTS_URL, "more")
COMMENT_IN_REVIEW_URL = url_path(COMMENTS_URL, "in_review")
COMMENT_ID_URL = url_path(COMMENTS_URL, f"<int:{PK_PARAM_NAME}>")
COMMENT_SLUG_URL = url_path(COMMENTS_URL, f"<slug:{SLUG_PARAM_NAME}>")
COMMENT_LIKE_ID_URL = url_path(COMMENT_ID_URL, "like")
COMMENT_HIDE_ID_URL = url_path(COMMENT_ID_URL, "hide")
COMMENT_REPORT_ID_URL = url_path(COMMENT_ID_URL, "report")
COMMENT_COMMENT_ID_URL = url_path(COMMENT_ID_URL, "comment")
COMMENT_FOLLOW_ID_URL = url_path(COMMENT_ID_URL, "follow")
COMMENT_REVIEW_STATUS_ID_URL = url_path(COMMENT_ID_URL, "review_status")
COMMENT_REVIEW_DECISION_ID_URL = url_path(COMMENT_ID_URL, "review_decision")

# convention is opinion route names begin with 'opinion'
OPINIONS_ROUTE_NAME = "opinions"
OPINION_NEW_ROUTE_NAME = "opinion_new"
OPINION_SEARCH_ROUTE_NAME = "opinion_search"
OPINION_FOLLOWED_ROUTE_NAME = "opinion_followed"
OPINION_IN_REVIEW_ROUTE_NAME = "opinion_in_review"
OPINION_ID_ROUTE_NAME = "opinion_id"
OPINION_SLUG_ROUTE_NAME = "opinion_slug"
SINGLE_OPINION_ROUTE_NAMES = [OPINION_ID_ROUTE_NAME, OPINION_SLUG_ROUTE_NAME]
OPINION_PREVIEW_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_preview"
OPINION_STATUS_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_status"
OPINION_LIKE_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_like"
OPINION_HIDE_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_hide"
OPINION_PIN_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_pin"
OPINION_REPORT_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_report"
OPINION_COMMENT_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_comment"
OPINION_FOLLOW_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_follow"
OPINION_REVIEW_STATUS_ID_ROUTE_NAME = f"{OPINION_ID_ROUTE_NAME}_review_status"
OPINION_REVIEW_DECISION_ID_ROUTE_NAME = \
    f"{OPINION_ID_ROUTE_NAME}_review_decision"

# convention is comment route names begin with 'comment'
COMMENTS_ROUTE_NAME = "comments"
COMMENT_ID_ROUTE_NAME = "comment_id"
COMMENT_SLUG_ROUTE_NAME = "comment_slug"
SINGLE_COMMENT_ROUTE_NAMES = [COMMENT_ID_ROUTE_NAME, COMMENT_SLUG_ROUTE_NAME]
COMMENT_SEARCH_ROUTE_NAME = "comment_search"
COMMENT_MORE_ROUTE_NAME = "comment_more"
COMMENT_IN_REVIEW_ROUTE_NAME = "comment_in_review"
COMMENT_LIKE_ID_ROUTE_NAME = f"{COMMENT_ID_ROUTE_NAME}_like"
COMMENT_HIDE_ID_ROUTE_NAME = f"{COMMENT_ID_ROUTE_NAME}_hide"
COMMENT_REPORT_ID_ROUTE_NAME = f"{COMMENT_ID_ROUTE_NAME}_report"
COMMENT_COMMENT_ID_ROUTE_NAME = f"{COMMENT_ID_ROUTE_NAME}_comment"
COMMENT_FOLLOW_ID_ROUTE_NAME = f"{COMMENT_ID_ROUTE_NAME}_follow"
COMMENT_REVIEW_STATUS_ID_ROUTE_NAME = f"{COMMENT_ID_ROUTE_NAME}_review_status"
COMMENT_REVIEW_DECISION_ID_ROUTE_NAME = \
    f"{COMMENT_ID_ROUTE_NAME}_review_decision"

SINGLE_CONTENT_ROUTE_NAMES = SINGLE_OPINION_ROUTE_NAMES.copy()
SINGLE_CONTENT_ROUTE_NAMES.extend(SINGLE_COMMENT_ROUTE_NAMES)


ORDER_QUERY: str = 'order'              # opinion order
PAGE_QUERY: str = 'page'                # page number
PER_PAGE_QUERY: str = 'per-page'        # pagination per page
REORDER_QUERY: str = 'reorder'          # reordering of previous query
SEARCH_QUERY: str = 'search'            # search from search box in header
# Note: a search can have any of the following queries embedded in its
# value
ID_QUERY: str = 'id'                        # search id
STATUS_QUERY: str = 'status'                # search status
CONTENT_QUERY: str = 'content'              # search content
AUTHOR_QUERY: str = 'author'                # search author
ON_OR_AFTER_QUERY: str = 'on-or-after'      # search >= date
ON_OR_BEFORE_QUERY: str = 'on-or-before'    # search <= date
AFTER_QUERY: str = 'after'                  # search > date
BEFORE_QUERY: str = 'before'                # search < date
EQUAL_QUERY: str = 'date'                   # search == date
HIDDEN_QUERY: str = 'hidden'                # search hidden
PINNED_QUERY: str = 'pinned'                # search pinned
REPORT_QUERY: str = 'report'                # search report
# Opinion specific search queries
TITLE_QUERY: str = 'title'                  # search title
CATEGORY_QUERY: str = 'category'            # search category
# Comment specific search queries
OPINION_ID_QUERY: str = 'opinion_id'        # search opinion id
PARENT_ID_QUERY: str = 'parent_id'          # search comment parent id
COMMENT_DEPTH_QUERY: str = 'depth'          # comment level depth

# general
REFERENCE_QUERY: str = 'ref'                # reference
MODE_QUERY: str = 'mode'                    # mode
FILTER_QUERY: str = 'filter'                # filter
REVIEW_QUERY: str = 'review'                # review status

OPINION_PAGINATION_ON_EACH_SIDE = 1
OPINION_PAGINATION_ON_ENDS = 1

# permissions related
CLOSE_REVIEW_PERM = "close_review"
WITHDRAW_REVIEW_PERM = "withdraw_review"


# templates related
# templates/opinions/snippet/reactions.html
TEMPLATE_TARGET_ID = 'target_id'            # id of target opinion/comment
TEMPLATE_TARGET_SLUG = 'target_slug'        # slug of target opinion/comment
TEMPLATE_TARGET_AUTHOR = 'target_author'    # id of target author
TEMPLATE_TARGET_TYPE = 'target_type'        # type of target; opinion/comment
# list of Reaction (can be for opinion or comment)
TEMPLATE_REACTIONS = 'reactions'
TEMPLATE_REACTION_CTRLS = 'reaction_ctrls'  # dict of ReactionCtrl
TEMPLATE_COMMENT_BUNDLE = 'bundle'          # CommentBundle

# templates/opinions/opinion_view.html
# list of Reaction for opinion
TEMPLATE_OPINION_REACTIONS = 'opinion_reactions'
OPINION_FORM_CTX = 'opinion_form'
COMMENT_FORM_CTX = 'comment_form'
REPORT_FORM_CTX = 'report_form'
SUBMIT_URL_CTX = 'submit_url'
READ_ONLY_CTX = 'read_only'     # read-only mode
IS_PREVIEW_CTX = 'is_preview'   # preview mode
IS_REVIEW_CTX = 'is_review'     # review mode
VIEW_OK_CTX = 'view_ok'         # ok to view flag
OPINION_CTX = 'opinion'
COMMENT_CTX = 'comment'
STATUS_CTX = 'status'
COMMENTS_CTX = 'comments'
USER_CTX = 'user'
CONTENT_STATUS_CTX = "content_status"
OPINION_CONTENT_STATUS_CTX = "opinion_content_status"
UNDER_REVIEW_TITLE_CTX = "under_review_title"
UNDER_REVIEW_EXCERPT_CTX = "under_review_excerpt"
UNDER_REVIEW_OPINION_CTX = "under_review_opinion"
UNDER_REVIEW_COMMENT_CTX = "under_review_comment"
DELETED_CONTENT_CTX = "deleted_content"
HIDDEN_CONTENT_CTX = "hidden_content"
POPULARITY_CTX = "popularity"
OPINION_LIST_CTX = "opinion_list"
COMMENT_LIST_CTX = 'comment_list'
STATUS_BG_CTX = "status_bg"
REVIEW_BUTTON_CTX = "review_button"
REVIEW_BUTTON_TIPS_CTX = "review_button_tips"
IS_ASSIGNED_CTX = 'is_assigned'
REVIEW_RECORD_CTX = 'review_record'
REVIEW_FORM_CTX = 'review_form'
ACTION_URL_CTX = 'action_url'

# templates/opinions/snippet/comment_bundle.html
# list of Reaction for comment
TEMPLATE_COMMENT_REACTIONS = 'comment_reactions'

# templates/opinions/snippet/content_updates_message.html
COUNT_CTX = "count"
OPINION_REVIEWS_CTX = "opinion_reviews"
COMMENT_REVIEWS_CTX = "comment_reviews"
# templates/opinions/snippet/tagged_author_opinions.html
TAGGED_COUNT_CTX = "tagged_count"

# templates/opinions/opinion_feed.html
IS_FOLLOWING_FEED_CTX = "is_following_feed"
IS_CATEGORY_FEED_CTX = "is_category_feed"
IS_ALL_FEED_CTX = "is_all_feed"
FOLLOWED_CATEGORIES_CTX = "followed_categories"
CATEGORY_CTX = 'category'

# templates/opinions/help/search.html
SEARCH_TERMS_CTX = 'search_terms'
DATE_SEPARATORS_CTX = 'date_separators'
DATE_CTX = 'date'
REACTION_ITEMS_CTX = 'reaction_items'

# general
TITLE_CTX = 'title'                             # page title
PAGE_HEADING_CTX = 'page_heading'               # page heading display
LIST_HEADING_CTX = 'list_heading'               # list heading display
LIST_SUB_HEADING_CTX = 'list_sub_heading'       # list sub heading display
REPEAT_SEARCH_TERM_CTX = 'repeat_search_term'   # search term for query
NO_CONTENT_MSG_CTX = 'no_content_msg'           # no content message
NO_CONTENT_HELP_CTX = 'no_content_help'         # help text when no content
REDIRECT_CTX = "redirect"

REWRITES_PROP_CTX = 'rewrites'
ELEMENT_ID_CTX = 'element_id'
HTML_CTX = 'html'
MESSAGE_CTX = 'msg'

COMMENT_DATA_CTX = "comment_data"
COMMENT_OFFSET_CTX = "comment_offset"

# miscellaneous
ALL_FIELDS = 'all_fields'
ALL_CATEGORIES = 'All'

UNDER_REVIEW_TITLE = 'Under Review'
UNDER_REVIEW_EXCERPT = 'Content not available'
UNDER_REVIEW_OPINION_CONTENT = \
    'The content of this opinion is not currently available to view as it ' \
    'is under review.'
UNDER_REVIEW_COMMENT_CONTENT = \
    'The content of this comment is not currently available to view as it ' \
    'is under review.'
HIDDEN_COMMENT_CONTENT = 'The content of this comment has been hidden.'
DELETED_CONTENT = 'This content has been deleted.'
