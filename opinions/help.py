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
from dataclasses import dataclass
from datetime import datetime
from string import capwords

from opinions.constants import (
    STATUS_QUERY, SEARCH_TERMS_CTX, TITLE_QUERY, CONTENT_QUERY, AUTHOR_QUERY,
    CATEGORY_QUERY, PINNED_QUERY, HIDDEN_QUERY, ON_OR_AFTER_QUERY,
    ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY, EQUAL_QUERY,
    DATE_SEPARATORS_CTX, DATE_CTX, REACTION_ITEMS_CTX
)

# https://www.compart.com/en/unicode/block/U+2700
_CHECK_MARK = "\N{Heavy Check Mark}"
_X_MARK = "\N{Heavy Ballot X}"


@dataclass
class SearchTermItem:
    term: str
    desc: str
    example: str


def get_search_terms_help() -> dict:
    """
    Get the search terms help
    :return:
    """
    from opinions.enums import QueryStatus, Pinned, Hidden
    from opinions.models import Opinion
    from opinions.search import DATE_SEPARATORS

    terms = [
        choice.arg for choice in QueryStatus.ALL.listing()
    ]
    pinned = [
        choice.arg for choice in [Pinned.YES, Pinned.NO]
    ]
    hidden = [
        choice.arg for choice in [Hidden.YES, Hidden.NO]
    ]

    search_terms = [
        SearchTermItem(
            TITLE_QUERY,
            f'Title of opinion or part thereof.',
            f'{TITLE_QUERY}="interesting"'
        ),
        SearchTermItem(
            CONTENT_QUERY,
            f'Part of content of opinion.',
            f'{CONTENT_QUERY}="strange and wonderful"'
        ),
        SearchTermItem(
            AUTHOR_QUERY,
            f'Username of opinion author.',
            f'{AUTHOR_QUERY}="oscar_wilde"'
        ),
        SearchTermItem(
            STATUS_QUERY,
            f'Status of opinion. Valid options are; {", ".join(terms)}.',
            f'{STATUS_QUERY}="{QueryStatus.DRAFT.arg}"'
        ),
        SearchTermItem(
            CATEGORY_QUERY,
            f'Category of opinion.',
            f'{CATEGORY_QUERY}="climate change"'
        ),
        SearchTermItem(
            PINNED_QUERY,
            f'Your pinned status of opinions. '
            f'Valid options are; {", ".join(pinned)}.',
            f'{STATUS_QUERY}="{Pinned.YES.arg}"'
        ),
        SearchTermItem(
            HIDDEN_QUERY,
            f'Your hidden status of opinions. '
            f'Valid options are; {", ".join(hidden)}.',
            f'{STATUS_QUERY}="{Hidden.YES.arg}"'
        ),
    ]

    test_text = {
        ON_OR_AFTER_QUERY: 'on or after',
        ON_OR_BEFORE_QUERY: 'on or before',
        AFTER_QUERY: 'after',
        BEFORE_QUERY: 'before',
        EQUAL_QUERY: 'equal'
    }

    def format_now(sep: str):
        return datetime.now().strftime("%d$%m$%Y".replace("$", sep))

    search_terms.extend([
        SearchTermItem(
            query,
            f'Opinions with {capwords(Opinion.SEARCH_DATE_FIELD)} date {test_text[query]} search date.',
            f'{query}="{format_now(sep)}"'
        ) for query, sep in [
            (qterm, DATE_SEPARATORS[idx % len(DATE_SEPARATORS)])
            for idx, qterm in enumerate([
                ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY, EQUAL_QUERY
            ])
        ]
    ])

    date_separators = [f"'{sep}'" for sep in DATE_SEPARATORS]

    return {
        SEARCH_TERMS_CTX: search_terms,
        DATE_SEPARATORS_CTX:
            f"{', '.join(date_separators[:-1])} or {date_separators[-1]}",
        DATE_CTX: format_now(DATE_SEPARATORS[0])
    }


@dataclass
class ReactionItem:
    item: str
    desc: str
    opinion: str
    comment: str


def get_reactions_help() -> dict:
    """
    Get the reactions help
    :return:
    """
    from opinions.reactions import \
        OPINION_REACTIONS_LIST, COMMENT_REACTIONS_LIST, \
        ReactionsList

    def get_list(field):
        return OPINION_REACTIONS_LIST \
            if not getattr(OPINION_REACTIONS_LIST, field).is_empty else \
            COMMENT_REACTIONS_LIST

    def get_attr(field: str, listing: ReactionsList = None):
        return getattr(listing if listing else get_list(field), field, None)

    def get_icon(field: str, listing: ReactionsList = None):
        reaction = get_attr(field, listing if listing else get_list(field))
        return getattr(reaction, 'icon')

    def get_desc(field: str):
        opinion = get_attr(field, OPINION_REACTIONS_LIST)
        comment = get_attr(field, COMMENT_REACTIONS_LIST)
        if opinion:
            opinion = getattr(opinion, 'aria')
        if comment:
            comment = getattr(comment, 'aria')
        return f'{opinion} / {comment}' if opinion and comment else \
            opinion if opinion else comment

    def get_mark(field: str, listing: ReactionsList = None):
        return _X_MARK if getattr(
            listing if listing else get_list(field), field).is_empty \
            else _CHECK_MARK

    reactions = [
        ReactionItem(
            get_icon(reaction), get_desc(reaction),
            get_mark(reaction, OPINION_REACTIONS_LIST),
            get_mark(reaction, COMMENT_REACTIONS_LIST),
        ) for reaction in ReactionsList.ALL_FIELDS
    ]

    return {
        REACTION_ITEMS_CTX: reactions
    }
