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

# Script to load a set of standard opinions/comment to the database

import os
from datetime import datetime, MINYEAR, timezone, timedelta
from pathlib import Path
import re
import csv
import argparse

import environ
import psycopg2
from bs4 import BeautifulSoup

from categories import (
    STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW, STATUS_PUBLISHED,
    STATUS_DRAFT, STATUS_PREVIEW, STATUS_UNACCEPTABLE
)
from utils.models import SlugMixin

BASE_DIR = Path(__file__).resolve().parent.parent

USER_TABLE = 'user_user'
CATEGORY_TABLE = 'categories_category'
STATUS_TABLE = 'categories_status'
OPINIONS_TABLE = 'opinions_opinion'
OPINION_CATEGORIES_TABLE = 'opinions_opinion_categories'
COMMENTS_TABLE = 'opinions_comment'
REVIEWS_TABLE = 'opinions_review'

# from opinions.models.Opinion
OPINION_ATTRIB_SLUG_MAX_LEN: int = 50
OPINION_ATTRIB_EXCERPT_MAX_LEN: int = 150
COMMENT_ATTRIB_SLUG_MAX_LEN: int = OPINION_ATTRIB_SLUG_MAX_LEN

DFLT_DATE = datetime(MINYEAR, 1, 1, tzinfo=timezone.utc)

usernames = ['user1', 'user2', 'user3', 'mod1']
users_usernames = list(
    filter(lambda name: name.startswith('user'), usernames))
moderators_usernames = list(
    filter(lambda name: name.startswith('mod'), usernames))
user_ids = {}

# opinions csv
OPINIONS_CSV = 'data/opinions.csv'
# opinions csv columns
OPINION_USERNAME = 0
OPINION_CATEGORY = 1
OPINION_STATUS = 2
OPINION_TITLE = 3
OPINION_CONTENT = 4

SCRAPE = "scrape"
LIGHTHOUSE = "runlighthouse"
# views from views.js
preLoginViews = 'pre-login'
followingView = 'following'
categoryView = 'category'
opinionNewView = 'opinion-new'
opinionEditView = 'opinion-edit'
opinionDraftView = 'opinion-draft'
opinionPreviewView = 'opinion-preview'
opinionsListDraftView = 'opinions-list-draft'
opinionsListPreviewView = 'opinions-list-preview'
opinionsListReviewView = 'opinions-list-review'
opinionsMineView = 'opinions-mine'
opinionsPinnedView = 'opinions-pinned'
opinionsFollowedNewView = 'opinions-follow-new'
opinionsFollowedAllView = 'opinions-follow-all'
opinionsAll = 'opinions-all'
commentsReviewView = 'comments-review'
commentsMineView = 'comments-mine'
commentsAll = 'comments-all'
modOpinionsPendingView = 'mod-opinions-pending'
modOpinionsUnderView = 'mod-opinions-under'
modOpinionsUnacceptableView = 'mod-opinions-unacceptable'
modCommentsPendingView = 'mod-comments-pending'
modCommentsUnderView = 'mod-comments-under'
modCommentsUnacceptableView = 'mod-comments-unacceptable'
modOpinionReviewPreAssignView = 'mod-opinion-review-pre-assign'
modOpinionReviewPostAssignView = 'mod-opinion-review-post-assign'
modOpinionReviewUnacceptableView = 'mod-opinion-review-unacceptable'
modCommentReviewPreAssignView = 'mod-comment-review-pre-assign'
modCommentReviewPostAssignView = 'mod-comment-review-post-assign'
modCommentReviewUnacceptableView = 'mod-comment-review-unacceptable'
userProfileView = 'user-profile'
logoutView = 'logout'
USER_VIEWS = [
    preLoginViews,
    followingView,
    categoryView,
    opinionNewView,
    opinionEditView,
    opinionDraftView,
    opinionPreviewView,
    opinionsListDraftView,
    opinionsListPreviewView,
    opinionsListReviewView,
    opinionsMineView,
    opinionsPinnedView,
    opinionsFollowedNewView,
    opinionsFollowedAllView,
    opinionsAll,
    commentsReviewView,
    commentsMineView,
    commentsAll,
    userProfileView,
    logoutView,
]
MODERATOR_VIEWS = [
    modOpinionsPendingView,
    modOpinionsUnderView,
    modOpinionsUnacceptableView,
    modCommentsPendingView,
    modCommentsUnderView,
    modCommentsUnacceptableView,
    modOpinionReviewPreAssignView,
    modOpinionReviewPostAssignView,
    modOpinionReviewUnacceptableView,
    modCommentReviewPreAssignView,
    modCommentReviewPostAssignView,
    modCommentReviewUnacceptableView,
]
completed_views = set()

# options from scrape.js
opinionId = 'opinion_id'
opinionPreId = 'pending_opinion'
opinionPostId = 'under_opinion'
opinionNgId = 'fail_opinion'
commentPreId = 'pending_comment'
commentPostId = 'under_comment'
commentNgId = 'fail_comment'

view_options = {}
for view in [opinionEditView, opinionDraftView, opinionPreviewView]:
    view_options[view] = opinionId
view_options[modOpinionReviewPreAssignView] = opinionPreId
view_options[modOpinionReviewPostAssignView] = opinionPostId
view_options[modOpinionReviewUnacceptableView] = opinionNgId
view_options[modCommentReviewPreAssignView] = commentPreId
view_options[modCommentReviewPostAssignView] = commentPostId
view_options[modCommentReviewUnacceptableView] = commentNgId

VIEW_ARG_MARKER = '<view_arg>'
HOST_ARG_MARKER = '<host_arg>'

def parse_args():
    parser = argparse.ArgumentParser(
        prog = 'populate',
        description = 'Populate generated views for analysis of html')
    parser.add_argument('-up', '--user_password',
                        help='User password', default='password')
    parser.add_argument('-mp', '--mod_password',
                        help='Moderator password', default='password')
    parser.add_argument('-dv', '--db_var',
                        help='Name of environment variable containing '
                             'database connection string',
                        default='DATABASE_URL')
    default_host = 'http://127.0.0.1:8000/'
    parser.add_argument('-u', '--host',
                        help=f'Host url e.g. {default_host}',
                        default=default_host)
    args = parser.parse_args()
    return args

def process():
    env = environ.Env()
    # Take environment variables from .env file
    os.environ.setdefault('ENV_FILE', '.env')
    os.environ.setdefault('SB_HOST', 'http://127.0.0.1:8000/')
    environ.Env.read_env(
        os.path.join(BASE_DIR, env('ENV_FILE'))
    )

    args = parse_args()

    db_url = env(args.db_var)

    # ElephantSQL db names are chars, passwords can contain - and _
    regex = re.compile(rf'.*://(\w+):([\w_-]+)@([\w.]+)/(\w+).*', re.IGNORECASE)
    match = regex.match(db_url)
    if not match:
        print("Credentials not found. Did you set the env_file?")
        exit(1)

    db_name = match.group(4)
    db_user = match.group(1)
    db_host = match.group(3)
    db_password = match.group(2)

    connection = f"dbname='{db_name}' user='{db_user}' host='{db_host}' " \
                 f"password='{db_password}'"
    with psycopg2.connect(connection) as conn:
        with conn.cursor() as curs:
            # get the user id's for the required users
            curs.execute(f"SELECT id, username FROM {USER_TABLE};")
            users = curs.fetchall()
            for user in usernames:
                usr_list = list(filter(lambda usr: usr[1] == user, users))
                if len(usr_list) == 1:
                    user_ids[user] = usr_list[0][0]
                else:
                    raise ValueError(f"User {user} not found")

            # get required data
            published_status = get_status_id(curs, STATUS_PUBLISHED)
            pending_status = get_status_id(curs, STATUS_PENDING_REVIEW)
            under_status = get_status_id(curs, STATUS_UNDER_REVIEW)
            unacceptable_status = get_status_id(curs, STATUS_UNACCEPTABLE)

            # load opinions
            with open(OPINIONS_CSV, encoding='utf-8') as csvfile:
                # use | as quote char to avoid messing with " inside quotes
                opinion_reader = csv.reader(
                    csvfile, delimiter=',', quotechar='|')
                for row in opinion_reader:
                    if row[OPINION_USERNAME] not in user_ids:
                        raise ValueError(f"User {user} not found")
                    author_id = user_ids[row[OPINION_USERNAME]]

                    # get category
                    category = get_category_id(curs, row[OPINION_CATEGORY])

                    # get status
                    status = get_status_id(curs, row[OPINION_STATUS])

                    # save opinion
                    now = datetime.now(tz=timezone.utc)
                    opinion = save_opinion(
                        curs, row[OPINION_TITLE], row[OPINION_CONTENT],
                        status, author_id, now, category,
                        is_published=status == published_status)

                    # add comments
                    for _, user_id in user_ids.items():
                        if user_id == author_id:
                            continue

                        content = 'interesting' if user_id % 2 == 0 \
                            else 'boring'
                        content = f"That's {content}"

                        comment = save_comment(
                            curs, content, opinion, published_status, user_id,
                            now
                        )

                        for username, l1_user_id in user_ids.items():
                            if user_id in [author_id, user_id]:
                                continue

                            l1_content = 'agree' if l1_user_id % 2 == 0 \
                                else 'disagree'
                            l1_content = f"I {l1_content}"

                            save_comment(curs, l1_content, opinion,
                                         published_status, l1_user_id,
                                         now + timedelta(days=1), level=1,
                                         parent=comment)

            # save opinions of pre-publish status
            now = datetime.now(tz=timezone.utc)
            days = 1
            categories = get_all_category_ids(curs)
            idx = 0
            cmds = []
            for qs_status in [STATUS_DRAFT, STATUS_PREVIEW]:
                status = get_status_id(curs, qs_status)
                nodeview = opinionDraftView if qs_status == STATUS_DRAFT \
                    else opinionPreviewView

                for username, user_id in user_ids.items():
                    opinion = save_opinion(
                        curs, f'{qs_status} opinion by {username}',
                        f'{username} here, still a bit to go',
                        status, user_id, now + timedelta(days=days),
                        categories[idx % len(categories)],
                        is_published=status == published_status)
                    idx += 1

                    print(f'{qs_status} opinion by {username}: {opinion}')

                    for cmd_view in [nodeview, opinionEditView]:
                        if cmd_view in completed_views:
                            continue
                        cmds.append(
                            node_cmd(SCRAPE, cmd_view, user=username,
                                     password=args.user_password,
                                     opinion=opinion)
                        )
                        completed_views.add(cmd_view)

            # save opinion with multi-level comments
            username = users_usernames[0]
            commenters = users_usernames[1:]
            opinion = save_opinion(
                curs, f'This opinion by {username} has, multi-level comments',
                "Strange as it doesn't says much",
                published_status, user_ids[username],
                now + timedelta(days=days),
                categories[int(len(categories)/2)],
                is_published=status == published_status)

            comment = 0
            for level in range(14):
                comment = save_comment(
                    curs, f'Level {level} comment', opinion, published_status,
                    user_ids[commenters[level % len(commenters)]],
                    now + timedelta(days=days), level=level, parent=comment
                )
                days += 1

            # report opinion
            username = users_usernames[0]
            complainers = users_usernames[1:]

            opinion_views = {
                STATUS_PENDING_REVIEW: modOpinionReviewPreAssignView,
                STATUS_UNDER_REVIEW: modOpinionReviewPostAssignView,
                STATUS_UNACCEPTABLE: modOpinionReviewUnacceptableView
            }
            comment_views = {
                STATUS_PENDING_REVIEW: modCommentReviewPreAssignView,
                STATUS_UNDER_REVIEW: modCommentReviewPostAssignView,
                STATUS_UNACCEPTABLE: modCommentReviewUnacceptableView
            }

            for qs_status in [
                STATUS_PENDING_REVIEW, STATUS_UNDER_REVIEW,
                STATUS_UNACCEPTABLE
            ]:
                status = get_status_id(curs, qs_status)

                for complainer in complainers:
                    opinion = save_opinion(
                        curs, f'Very contentious according to '
                              f'{complainer} - {qs_status}',
                        f'{username} thinks people will complain',
                        published_status, user_ids[username],
                        now + timedelta(days=days),
                        categories[idx % len(categories)],
                        is_published=status == published_status)
                    days += 1

                    report_content(
                        curs, 'I disagree', status, user_ids[complainer],
                        now + timedelta(days=days), opinion=opinion,
                        reviewer_id=user_ids[moderators_usernames[0]] if
                        status in [under_status, unacceptable_status] else
                        None
                    )

                    print(f'{qs_status} opinion by {username} according to '
                          f'{complainer}: {opinion}')

                    cmd_view = opinion_views[qs_status]
                    if cmd_view not in completed_views:
                        cmds.append(
                            node_cmd(SCRAPE, cmd_view,
                                     user=moderators_usernames[0],
                                     password=args.mod_password,
                                     opinion=opinion)
                        )
                        completed_views.add(cmd_view)

                    # report comment
                    opinion = save_opinion(
                        curs, f'Contentious comments according to '
                              f'{complainer} - {qs_status}',
                        f'{username} thinks people will complain',
                        published_status, user_ids[username],
                        now + timedelta(days=days),
                        categories[idx % len(categories)],
                        is_published=status == published_status)
                    days += 1

                    commenter = list(
                        filter(lambda usr: usr != complainer, complainers))[0]
                    comment = save_comment(
                        curs, f'Contentious comment by {commenter}', opinion,
                        published_status, user_ids[commenter],
                        now + timedelta(days=days)
                    )

                    report_content(
                        curs, 'I disagree', status, user_ids[complainer],
                        now + timedelta(days=days), comment=comment,
                        reviewer_id=user_ids[moderators_usernames[0]] if
                        status in [under_status, unacceptable_status] else
                        None
                    )

                    print(f'Opinion with {qs_status} comment by {username} '
                          f'according to {complainer}: {opinion}')

                    cmd_view = comment_views[qs_status]
                    if cmd_view not in completed_views:
                        cmds.append(
                            node_cmd(SCRAPE, cmd_view,
                                     user=moderators_usernames[0],
                                     password=args.mod_password,
                                     comment=comment)
                        )
                        completed_views.add(cmd_view)

    make_script(args, SCRAPE, cmds, host=args.host)


def save_opinion(
    curs, title: str, content: str, status: int, user_id: int,
    when: datetime, category: [str, int], is_published: bool = False
) -> int:

    slug = SlugMixin.generate_slug(OPINION_ATTRIB_SLUG_MAX_LEN, title)
    fields = 'title, content, slug, created, updated, published, ' \
             'status_id, user_id, excerpt'
    values = (
        title,  # title
        content,  # content
        slug,  # slug
        when,  # created
        when,  # updated
        when if is_published else DFLT_DATE,  # published
        str(status),  # status_id
        str(user_id),  # user_id
        generate_excerpt(content)   # excerpt
    )
    opinion = insert_content(curs, fields, values, OPINIONS_TABLE, slug=slug)

    # save category info
    if isinstance(category, str):
        category = get_category_id(curs, category)
    sql = f"INSERT INTO {OPINION_CATEGORIES_TABLE} " \
          f"(opinion_id, category_id) VALUES (%s,%s);"
    curs.execute(sql, (opinion, category))

    return opinion


def save_comment(curs, content: str, opinion: int, status: int, user_id: int,
                 when: datetime, level: int = 0, parent: int = 0):

    slug = SlugMixin.generate_slug(
        COMMENT_ATTRIB_SLUG_MAX_LEN, content)
    fields = 'content, parent, slug, created, updated, opinion_id, ' \
             'status_id, user_id, level, published'
    values = (
        content,                # content
        parent,                 # parent
        slug,                   # slug
        when,                   # created
        when,                   # updated
        opinion,                # opinion_id
        status,                 # status_id
        user_id,                # user_id
        level,                  # level
        when,                   # published
    )
    return insert_content(curs, fields, values, COMMENTS_TABLE, slug=slug)


def insert_content(curs, fields: str, values: tuple, table: str,
                   slug: str = None):

    sql = f"INSERT INTO {table} ({fields}) " \
          f"VALUES ({','.join(['%s' for _ in range(len(values))])});"
    curs.execute(sql, values)

    # get id of new content
    content = None
    if slug:
        curs.execute(f"SELECT id FROM {table} WHERE "
                     f"slug='{slug}';")
        content = curs.fetchone()
        if not content:
            raise ValueError(f"Content {slug} not found")
        content = content[0]

    return content


def report_content(curs, reason: str, status: int, requested_id: int,
                   when: datetime, opinion: int = None, comment: int = None,
                   reviewer_id: int = 0,
                   is_resolved: bool = False):

    fields = 'reason, created, updated, resolved, requested_id, ' \
             'status_id, is_current'
    values = [
        reason,         # reason
        when,           # created
        when,           # updated
        when if is_resolved else DFLT_DATE,  # resolved
        requested_id,   # requested_id
        status,         # status_id
        True,           # is_current
    ]
    if reviewer_id:
        fields = f'{fields}, reviewer_id'
        values.append(reviewer_id)    # reviewer_id
    if opinion:
        fields = f'{fields}, opinion_id'
        values.append(opinion)        # opinion_id
    elif comment:
        fields = f'{fields}, comment_id'
        values.append(comment)        # comment_id

    insert_content(curs, fields, tuple(values), REVIEWS_TABLE)

    # mark other records as old
    curs.execute(f"UPDATE {REVIEWS_TABLE} SET is_current=false WHERE "
                 f"requested_id={requested_id} AND "
                 f"opinion_id={opinion if opinion else 'null'} AND "
                 f"comment_id={comment if comment else 'null'};")


def get_status_id(curs, name: str):
    curs.execute(f"SELECT id FROM {STATUS_TABLE} WHERE "
                 f"LOWER(name)=LOWER('{name}');")
    status = curs.fetchone()
    if not status:
        raise ValueError(f"Status {name} not found")
    return status[0]


def get_category_id(curs, name: str):
    curs.execute(f"SELECT id FROM {CATEGORY_TABLE} WHERE "
                 f"LOWER(name)=LOWER('{name}');")
    category = curs.fetchone()
    if not category:
        raise ValueError(f"Category {name} not found")
    return category[0]


def get_all_category_ids(curs):
    curs.execute(f"SELECT id FROM {CATEGORY_TABLE};")
    categories = curs.fetchall()
    return [category[0] for category in categories]


def generate_excerpt(content: str):
    """
    Generate an excerpt
    :param content: content to generate excerpt from
    :return: excerpt string
    """
    soup = BeautifulSoup(content, features="lxml")
    text = soup.get_text()
    if len(text) > OPINION_ATTRIB_EXCERPT_MAX_LEN:
        text = f'{text[:OPINION_ATTRIB_EXCERPT_MAX_LEN-1]}…'
    return text


def node_cmd(script: str, cmd_view: str, user: str = None,
             password: str = None, opinion: int = None, comment: int = None):
    extra = {}
    if cmd_view in [
        opinionEditView, opinionDraftView, opinionPreviewView,
        modOpinionReviewPreAssignView, modOpinionReviewPostAssignView,
        modOpinionReviewUnacceptableView
    ]:
        extra[view_options[cmd_view]] = opinion
    elif cmd_view in [
        modCommentReviewPreAssignView, modCommentReviewPostAssignView,
        modCommentReviewUnacceptableView
    ]:
        extra[view_options[cmd_view]] = comment

    if not password:
        password = 'password'
    credentials = f'-u {user} -p {password} ' if user else ''
    cmd = f'node .\\{script}.js -b {HOST_ARG_MARKER} {credentials} ' \
          f'-{VIEW_ARG_MARKER} {cmd_view}'
    for key, val in extra.items():
        cmd = f'{cmd} --{key} {val}'
    return cmd


def make_script(args, script: str, cmds: list[str],
                host: str = 'http://127.0.0.1:8000/'):
    view_arg = "v" if script == SCRAPE else "r"
    indent = " " * 4

    cmd_list = [
        node_cmd(script, cmd_view, user=users_usernames[0],
                 password=args.user_password)
        for cmd_view in USER_VIEWS if cmd_view not in completed_views
    ]
    cmd_list.extend([
        node_cmd(script, cmd_view, user=moderators_usernames[0],
                 password=args.mod_password)
        for cmd_view in MODERATOR_VIEWS if cmd_view not in completed_views
    ])

    with open(f'run_{script}.py', 'w', encoding='utf-8') as file:
        file.write('import subprocess\n')
        file.write('cmds = [\n')
        for cmd in cmd_list:
            updated = cmd.replace(VIEW_ARG_MARKER, view_arg) \
                .replace(HOST_ARG_MARKER, host)
            file.write(f'{indent}"{updated}",\n')
        file.write(']\n')
        file.write('for cmd in cmds:\n')
        file.write(f'{indent}result = subprocess.run(cmd.split(), '
                   f'capture_output=True)\n')
        file.write(f'{indent}print(result.stdout.decode("utf-8"))\n')


if __name__ == "__main__":
    process()
