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
from copy import copy
from dataclasses import dataclass
from enum import Enum, auto


class HandleType(Enum):
    """ Reaction handler types enum """
    NONE = auto()
    AJAX = auto()
    MODAL = auto()


class UrlType(Enum):
    """ Url types enum """
    NONE = 'none'
    ID = 'id'
    SLUG = 'slug'


class HtmlTag:
    """ Class representing a HTML tag """
    tag: str
    content: str
    attribs: dict[str, str]

    CLASS_ATTRIB = 'clazz'

    def __init__(self, **kwargs):
        self.attribs = {}
        for key, val in kwargs.items():
            key = key.lower()
            if key in ['tag', 'content']:
                setattr(self, key, val)
            else:
                self.attribs[HtmlTag.attrib(key)] = val

    @staticmethod
    def attrib(name: str):
        """
        Convert an attribute name is necessary
        :param name: name
        :return: converted name
        """
        return 'class' if name == HtmlTag.CLASS_ATTRIB else name

    @staticmethod
    def of(tag: str, **kwargs):
        """
        Create a tag
        :param tag: tag name
        :param kwargs: tag attributes
        :return: HtmlTag
        """
        tag_args = kwargs.copy()
        tag_args['tag'] = tag.lower()
        return HtmlTag(**tag_args)

    @staticmethod
    def span(**kwargs):
        """
        Create a `span` tag
        :param kwargs: tag attributes
        :return: HtmlTag
        """
        return HtmlTag.of('span', **kwargs)

    @staticmethod
    def i(**kwargs):
        """
        Create an `i` tag
        :param kwargs: tag attributes
        :return: HtmlTag
        """
        return HtmlTag.of('i', **kwargs)

    def __str__(self):
        """ Render to a html string """
        attrib_str = ' '.join(list(
            map(lambda item: f'{item[0]}="{item[1]}"', self.attribs.items())
        ))
        return f'<{self.tag}{f" {attrib_str}" if attrib_str else ""}>' \
               f'{self.content if hasattr(self, "content") else ""}' \
               f'</{self.tag}>'


class Reaction:
    """ Class representing a reaction element """
    name: str           # reaction name
    identifier: str     # identifier, to generate ids for reaction buttons
    icon: str           # icon to use
    aria: str           # aria label
    handle_type: HandleType    # type; MODAL or AJAX
    url: str            # url
    url_type: UrlType   # type; ID or SLUG
    option: str         # selected option
    modal: str          # target modal
    field: str          # ReactionsList field

    def __init__(self, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(self, key.lower(), val)

    @classmethod
    def ajax_of(cls, **kwargs) -> object:
        """
        Create ajax Reaction, allowed keywords are
        :name: reaction name
        :identifier: identifier
        :icon: icon html to use
        :aria: aria label
        :url: url
        :option: selected option
        :return: Reaction instance
        """
        reaction_kwargs = kwargs.copy()
        reaction_kwargs['handle_type'] = HandleType.AJAX
        return Reaction(**reaction_kwargs)

    @classmethod
    def modal_of(cls, **kwargs) -> object:
        """
        Create modal Reaction, allowed keywords are
        :name: reaction name
        :identifier: identifier
        :icon: icon html to use
        :aria: aria label
        :url: url
        :option: selected option
        :modal: target modal
        :return: Reaction instance
        """
        reaction_kwargs = kwargs.copy()
        reaction_kwargs['handle_type'] = HandleType.MODAL
        if 'option' not in reaction_kwargs:
            reaction_kwargs['option'] = ''
        return Reaction(**reaction_kwargs)

    @classmethod
    def empty(cls) -> object:
        """
        Create empty Reaction
        :return: Reaction instance
        """
        return Reaction(**{
            'name': '', 'identifier': '', 'icon': '', 'aria': '',
            'handle_type': HandleType.NONE, 'url': '',
            'url_type': UrlType.NONE, 'option': '', 'modal': '', 'field': ''
        })

    def set_icon(self, icon: HtmlTag):
        """
        Set the icon from a fontawesome `i` tag
        :param icon: html `i` tag
        """
        if icon.tag != 'i':
            raise ValueError(f'Expecting `i` tag, received {icon}')

        # tried adding support for stacked fontawesome icons but the css
        # for the stacking threw the alignment and sizing out, stick with
        # single icons for now

        # content of span
        span_attrib = {'content': str(icon)}

        if self.is_modal:
            # https://getbootstrap.com/docs/5.2/components/modal/
            span_attrib['data-bs-toggle'] = 'modal'
            span_attrib['data-bs-target'] = f'{self.modal}'
            if self.option:
                span_attrib['data-bs-option'] = f'{self.option}'
        else:
            span_attrib['data-bs-option'] = f'{self.option}'

        self.icon = str(HtmlTag.span(**span_attrib))

        return self

    def copy(self, **kwargs):
        """
        Get an updated copy of this object
        :param kwargs: updates to apply to new object
        :return: new object
        """
        new_copy = copy(self)
        for key, val in kwargs.items():
            setattr(new_copy, key.lower(), val)
        return new_copy

    @property
    def is_ajax(self):
        """ Is AJAX type """
        return self.handle_type == HandleType.AJAX

    @property
    def is_modal(self):
        """ Is MODAL type """
        return self.handle_type == HandleType.MODAL

    @property
    def is_empty(self):
        """ Is NONE type """
        return self.handle_type == HandleType.NONE

    @property
    def is_id_url(self):
        """ Is ID type """
        return self.url_type == UrlType.ID

    @property
    def is_slug_url(self):
        """ Is SLUG type """
        return self.url_type == UrlType.SLUG

    @property
    def is_no_url(self):
        """ Is NONE type """
        return self.url_type == UrlType.NONE

    def __str__(self) -> str:
        return f'{type(self).__name__}: {self.name} {self.identifier}'


@dataclass
class ReactionCtrl:
    """ Data class for reaction element control """
    selected: bool  # is selected flag
    disabled: bool  # reaction disabled
    visible: bool   # reaction visible


@dataclass
class ContentStatus:
    """ Review status for Opinion/Comment """

    reported: bool      # was reported
    viewable: bool      # ok to view (with respect to reporting)
    review_wip: bool    # review in progress
    hidden: bool        # was hidden (has precedence over viewable)

    @property
    def view_ok(self):
        return self.viewable and not self.hidden


ContentStatus.VIEW_OK = ContentStatus(
    reported=False, viewable=True, review_wip=False, hidden=False)
