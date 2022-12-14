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
import json
from http import HTTPStatus
from unittest import skip

from bs4 import BeautifulSoup
from django.http import HttpResponse

from categories import (
    REACTION_AGREE,
    REACTION_DISAGREE, REACTION_PIN, REACTION_UNPIN, REACTION_FOLLOW,
    REACTION_UNFOLLOW
)
from categories.models import Status
from opinions.constants import (
    STATUS_QUERY, OPINION_LIKE_ID_ROUTE_NAME, OPINION_PIN_ID_ROUTE_NAME,
    OPINION_FOLLOW_ID_ROUTE_NAME, ELEMENT_ID_CTX
)
from opinions.data_structures import Reaction
from opinions.models import Opinion
from opinions.reactions import OPINION_REACTIONS_LIST
from opinions.templatetags.reaction_button_id import reaction_button_id
from opinions.templatetags.reaction_ul_id import reaction_ul_id
from opinions.enums import ReactionStatus
from soapbox import OPINIONS_APP_NAME
from utils import reverse_q, namespaced_url
from .base_opinion_test_cls import BaseOpinionTest
from .opinion_mixin_test_cls import OpinionMixin
from ..soup_mixin import SoupMixin

LIKE_REACTIONS = [REACTION_AGREE, REACTION_DISAGREE]
LIKE_PARAMS = {
    REACTION_AGREE: ReactionStatus.AGREE,
    REACTION_DISAGREE: ReactionStatus.DISAGREE,
}
PIN_REACTIONS = [REACTION_PIN, REACTION_UNPIN]
PIN_PARAMS = {
    REACTION_PIN: ReactionStatus.PIN,
    REACTION_UNPIN: ReactionStatus.UNPIN,
}
FOLLOW_REACTIONS = [REACTION_FOLLOW, REACTION_UNFOLLOW]
FOLLOW_PARAMS = {
    REACTION_FOLLOW: ReactionStatus.FOLLOW,
    REACTION_UNFOLLOW: ReactionStatus.UNFOLLOW,
}


class TestOpinionReaction(SoupMixin, OpinionMixin, BaseOpinionTest):
    """
    Test opinion page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super(TestOpinionReaction, cls).setUpTestData()

    def test_not_logged_in_access(self):
        """ Test must be logged in to set opinion reaction """
        opinion = TestOpinionReaction.opinions[0]
        url = reverse_q(
            namespaced_url(
                OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME),
            args=[opinion.id],
            query_kwargs={
                STATUS_QUERY: ReactionStatus.AGREE.arg
            })
        response = self.client.patch(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_opinion_like_patch(self):
        """
        Test setting like/unlike status of opinion
        """
        opinion = TestOpinionReaction.opinions[0]
        logged_in_user = TestOpinionReaction.login_user(
            self, TestOpinionReaction.get_other_user(opinion.user))

        self.assertNotEqual(logged_in_user, opinion.user)

        # like statuses and query params
        statuses = list(
            Status.objects.filter(name__in=LIKE_REACTIONS)
        )
        # a - d
        a_d = list(map(lambda s: LIKE_PARAMS[s.name], statuses))
        # d - a
        d_a = a_d.copy()
        d_a.reverse()
        # a - d => d on
        query_params = a_d.copy()
        # d => all off
        query_params.append(a_d[-1])
        # d - a => a on
        query_params.extend(d_a)
        # a => all off
        query_params.append(a_d[0])

        for index in range(len(query_params)):
            with self.subTest(
                    f'status {query_params[index].arg} index {index}'):
                url = reverse_q(
                    namespaced_url(
                        OPINIONS_APP_NAME, OPINION_LIKE_ID_ROUTE_NAME),
                    args=[opinion.id],
                    query_kwargs={
                        STATUS_QUERY: query_params[index].arg
                    })
                response = self.client.patch(url)

                if index == len(statuses) or index == len(query_params) - 1:
                    # d => all off or a => all off i.e. toggle setting
                    agree = False
                    disagree = False
                else:
                    # set setting
                    agree = query_params[index] == ReactionStatus.AGREE
                    disagree = query_params[index] == ReactionStatus.DISAGREE
                self.verify_opinion_reactions_status(
                    opinion, response, [
                        (OPINION_REACTIONS_LIST.agree, agree),
                        (OPINION_REACTIONS_LIST.disagree, disagree)
                    ], HTTPStatus.OK)

    def test_opinion_pin_patch(self):
        """
        Test setting pin/unpin status of opinion
        """
        opinion = TestOpinionReaction.opinions[0]
        logged_in_user = TestOpinionReaction.login_user(
            self, TestOpinionReaction.get_other_user(opinion.user))

        self.assertNotEqual(logged_in_user, opinion.user)

        # like statuses and query params
        statuses = list(
            Status.objects.filter(name__in=PIN_REACTIONS)
        )
        # p - p => p
        query_params = [
            PIN_PARAMS[statuses[0].name] for _ in range(2)
        ]
        # u - u => u
        query_params.extend([
            PIN_PARAMS[statuses[1].name] for _ in range(2)
        ])

        for index, param in enumerate(query_params):
            with self.subTest(
                    f'status {param.arg} index {index}'):
                url = reverse_q(
                    namespaced_url(
                        OPINIONS_APP_NAME, OPINION_PIN_ID_ROUTE_NAME),
                    args=[opinion.id],
                    query_kwargs={
                        STATUS_QUERY: param.arg
                    })
                response = self.client.patch(url)

                pinned = param == ReactionStatus.PIN
                # ok if changed, no content if no change
                code = HTTPStatus.OK if index % 2 == 0 else\
                    HTTPStatus.NO_CONTENT
                self.verify_opinion_reactions_status(
                    opinion, response, [
                        (OPINION_REACTIONS_LIST.unpin
                         if pinned else OPINION_REACTIONS_LIST.pin, pinned)
                    ], code)

    def test_opinion_follow_patch(self):
        """
        Test setting follow/unfollow status of opinion
        """
        opinion = TestOpinionReaction.opinions[0]
        logged_in_user = TestOpinionReaction.login_user(
            self, TestOpinionReaction.get_other_user(opinion.user))

        self.assertNotEqual(logged_in_user, opinion.user)

        # like statuses and query params
        statuses = list(
            Status.objects.filter(name__in=FOLLOW_REACTIONS)
        )
        # f - f => f
        query_params = [
            FOLLOW_PARAMS[statuses[0].name] for _ in range(2)
        ]
        # u - u => u
        query_params.extend([
            FOLLOW_PARAMS[statuses[1].name] for _ in range(2)
        ])

        for index, param in enumerate(query_params):
            with self.subTest(
                    f'status {param.arg} index {index}'):
                url = reverse_q(
                    namespaced_url(
                        OPINIONS_APP_NAME, OPINION_FOLLOW_ID_ROUTE_NAME),
                    args=[opinion.id],
                    query_kwargs={
                        STATUS_QUERY: param.arg
                    })
                response = self.client.patch(url)

                follow = param == ReactionStatus.FOLLOW
                # ok if changed, no content if no change
                code = HTTPStatus.OK if index % 2 == 0 else\
                    HTTPStatus.NO_CONTENT
                self.verify_opinion_reactions_status(
                    opinion, response, [
                        (OPINION_REACTIONS_LIST.unfollow
                         if follow else OPINION_REACTIONS_LIST.follow,
                         follow)
                    ], code)

    def verify_opinion_reactions_status(
                self, opinion: Opinion, response: HttpResponse,
                reaction_selected: list[tuple[Reaction, bool]],
                code: HTTPStatus
            ):
        """
        Verify opinion like status
        :param opinion: opinion
        :param response: http response
        :param reaction_selected: list of reactions and statuses to verify
        :param code: expected response status code
        """
        self.assertEqual(response.status_code, code)
        if code != HTTPStatus.NO_CONTENT:
            result = json.loads(response.content)
            self.assertEqual(result[ELEMENT_ID_CTX],
                             reaction_ul_id('opinion', opinion.id))

            soup = BeautifulSoup(result['html'], features="lxml")
            tags = soup.find_all('button')

            for reaction, selected in reaction_selected:
                button_id = reaction_button_id(reaction, opinion.id)
                button = SoupMixin.find_tag(
                    self, tags, lambda tag: tag['id'] == button_id)
                if selected:
                    # check selected
                    self.assertTrue(
                        SoupMixin.in_tag_attr(
                            button, 'class', 'reactions-selected'),
                        f'{reaction.name} not selected'
                    )
                else:
                    # check not selected
                    self.assertTrue(
                        SoupMixin.not_in_tag_attr(
                            button, 'class', 'reactions-selected'),
                        f'{reaction.name} selected'
                    )
