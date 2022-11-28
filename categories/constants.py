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

# common field names
NAME_FIELD = "name"
DESCRIPTION_FIELD = "description"

# status display names
STATUS_DRAFT = 'Draft'
STATUS_PUBLISHED = 'Published'
STATUS_PREVIEW = 'Preview'
STATUS_WITHDRAWN = 'Withdrawn'              # review request withdrawn
STATUS_PENDING_REVIEW = 'Pending Review'    # pending review following request
STATUS_UNDER_REVIEW = 'Under Review'        # under review
STATUS_APPROVED = 'Approved'            # review approved, content needs work
""" STATUS_APPROVED is deprecated use STATUS_UNACCEPTABLE instead """
STATUS_REJECTED = 'Rejected'            # review rejected, content ok
""" STATUS_REJECTED is deprecated use STATUS_ACCEPTABLE instead """
STATUS_UNACCEPTABLE = 'Unacceptable'    # review, content needs work
STATUS_ACCEPTABLE = 'Acceptable'        # review, content ok
STATUS_DELETED = 'Deleted'              # content deleted
# status combinations display names
STATUS_ALL = 'All'
STATUS_PRE_PUBLISH = 'Prepublish'           # draft or preview
STATUS_REVIEW_WIP = 'Review In Progress'    # pending review or under review
STATUS_REVIEW = 'Review'                    # all review-related statuses
STATUS_REVIEW_OVER = 'Review Complete'      # review acceptable/unacceptable

CATEGORY_UNASSIGNED = 'Unassigned'

# reaction statuses display names
REACTION_AGREE = 'Agree'
REACTION_DISAGREE = 'Disagree'
REACTION_HIDE = 'Hide'
REACTION_SHOW = 'Show'
REACTION_PIN = 'Pin'
REACTION_UNPIN = 'Unpin'
REACTION_FOLLOW = 'Follow'
REACTION_UNFOLLOW = 'Unfollow'
REACTION_SHARE = 'Share'
REACTION_REPORT = 'Report'
REACTION_COMMENT = 'Comment'
REACTION_DELETE = 'Delete'
