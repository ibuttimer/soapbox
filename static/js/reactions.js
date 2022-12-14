/*
 * MIT License
 *
 * Copyright (c) 2022 Ian Buttimer
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 */

/**
 * Update react status of current opinion
 * :param event: click event
 * :param done_func: reaction specific done handler function
 */
function updateReactStatus(event, done_func) {
    // hide tooltip
    $("#" + event.currentTarget.id).tooltip("hide");

    const reaction = get_react_info(event)

    $.ajax({
        url: reaction.url + "?status=" + reaction.option,
        method: 'patch',
        headers: {
            'X-CSRFTOKEN': csrfToken()
        }
    }).done(function(data) {
        done_func(data);

        // set click handlers for reactions
        setReactionHandlers();
        enableTooltips();
    });
}

/**
 * Update react status of current opinion
 * :param event: click event
 * :param done_func: reaction specific done handler function
 */
function getCommentEdit(event, done_func) {
    // hide tooltip
    $("#" + event.currentTarget.id).tooltip("hide");

    const reaction = get_react_info(event)

    document.location.href = `${reaction.url}?mode=edit`;
}

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();

/**
 * Get react info
 * :param event: click event
 */
function get_react_info(event) {
    // ids are of the form 'id--react-<action>-<type>-<id>' e.g. 'id--react-agree-opinion-1'
    const split = event.currentTarget.attributes['id'].textContent.split('-')
    let data_bs_option = '';
    if (event.currentTarget.firstElementChild.attributes.hasOwnProperty('data-bs-option')) {
        data_bs_option = event.currentTarget.firstElementChild.attributes['data-bs-option'].textContent
    }
    return {
        // href is on the button
        url: event.currentTarget.attributes['data-bs-href'].textContent,
        // title is on the button
        title: event.currentTarget.attributes['data-bs-title'].textContent,
        // type is taken from the button id
        type: split[4],
        // status option is on the span in the button (see reactions.html)
        option: data_bs_option,
        // status option is the action to perform, e.g. 'show'/'hide'/etc. i.e. ReactionStatus.XXX.arg
        action: data_bs_option,
        submit: capitalize(data_bs_option)
    };
}
/**
 * Set react info vars
 * :param event: click event
 * :param ids: object with keys matching those returned by get_react_info()
 *             and values as ids of element to be set
 * :param baseUrl: base url to prepend to url value
 */
function set_react_info_vars(event, ids, baseUrl = undefined) {
    const reaction = get_react_info(event)
    for (const [key, selector] of Object.entries(ids)) {
        let value = reaction[key];
        if (key === 'url' && baseUrl !== undefined) {
            value = baseUrl + value;
        }
        $(selector).text(value);
    }
}

/**
 * Update like/unlike status of current opinion
 * :param event: click event
 */
function updateOnOffReaction(event) {
    updateReactStatus(event, redirect_rewrite_response_handler);
}

// Reaction buttons have the general form: "id--react-<action>-<type>-<id>"
// where: action is [agree|disagree|comment|follow|unfollow|share|hide|unhide|pin|unpin|report]
//        type is [opinion|comment]
//        id is id of target opinion/comment

// Reaction buttons for comments are named 'id--react-comment-....'
const commentReactionsSelector = "button[id^='id--react-comment']";
// Reaction buttons for like are named 'id--react-agree-....'
const likeReactionsSelector = "button[id^='id--react-agree']";
// Reaction buttons for unlike are named 'id--react-disagree-....'
const unlikeReactionsSelector = "button[id^='id--react-disagree']";
// Reaction buttons for hide are named 'id--react-hide-....'
const hideReactionsSelector = "button[id^='id--react-hide']";
// Reaction buttons for hide are named 'id--react-show-....'
const showReactionsSelector = "button[id^='id--react-show']";
// Reaction buttons for pin are named 'id--react-pin-....'
const pinReactionsSelector = "button[id^='id--react-pin']";
// Reaction buttons for unpin are named 'id--react-unpin-....'
const unpinReactionsSelector = "button[id^='id--react-unpin']";
// Reaction buttons for follow are named 'id--react-follow-....'
const followReactionsSelector = "button[id^='id--react-follow']";
// Reaction buttons for unfollow are named 'id--react-unfollow-....'
const unfollowReactionsSelector = "button[id^='id--react-unfollow']";
// Reaction buttons for report are named 'id--react-report-....'
const reportReactionsSelector = "button[id^='id--react-report']";
// Reaction buttons for share are named 'id--react-share-....'
const shareReactionsSelector = "button[id^='id--react-share']";
// Reaction buttons for delete are named 'id--react-delete-....'
const deleteReactionsSelector = "button[id^='id--react-delete']";
// Reaction buttons for comments are named 'id--react-edit-....'
const editCommentReactionsSelector = "button[id^='id--react-edit']";

/* Set the click handlers for reactions */
function setReactionHandlers() {
    /* TODO removing and adding all the handlers is unnecessary */

    // remove old handlers to prevent duplicates
    for (let selector of [
        commentReactionsSelector, likeReactionsSelector, unlikeReactionsSelector,
        hideReactionsSelector, showReactionsSelector,
        pinReactionsSelector, unpinReactionsSelector,
        followReactionsSelector, unfollowReactionsSelector,
        reportReactionsSelector, shareReactionsSelector,
        deleteReactionsSelector, editCommentReactionsSelector
    ]) {
        $(selector).off();
    }

    // add new handlers
    $(commentReactionsSelector).on('click', (event) => {
        // set the submit url for comments
        set_react_info_vars(event, {
            url: commentSubmitUrlSelector
        });
    });
    $(reportReactionsSelector).on('click', (event) => {
        // set the submit url for reports
        set_react_info_vars(event, {
            url: reportSubmitUrlSelector,
            title: "#id--report-modal-heading"
        });
    });
    $(deleteReactionsSelector).on('click', (event) => {
        // set the delete url for comments
        set_react_info_vars(event, {
            url: commentDeleteUrlSelector
        });

        // display confirmation modal
        $(commentDeleteConfirmModalSelector).modal('show');
    });
    $(editCommentReactionsSelector).on('click', (event) => {
        getCommentEdit(event, function(data) {
            /* TODO handle edit in comment modal */
        });
    });
    $(shareReactionsSelector).on('click', (event) => {
        // set the share url for share
        const baseUrl = window.location.href.slice(0, window.location.href.indexOf(window.location.pathname))
        set_react_info_vars(event, {
            url: "#id--share-url",
            title: "#id--share-modal-heading"
        }, baseUrl);
    });
    for (let selector of [
        // update like/unlike status
        likeReactionsSelector, unlikeReactionsSelector,
        // update pin/unpin status
        pinReactionsSelector, unpinReactionsSelector,
        // update follow/unfollow status
        followReactionsSelector, unfollowReactionsSelector,
    ]) {
        $(selector).on('click', (event) => {
            updateOnOffReaction(event);
        });
    }
    for (let selector of [hideReactionsSelector, showReactionsSelector]) {
        $(selector).on('click', (event) => {
            // set the submit url/option/title for hide/show
            set_react_info_vars(event, {
                // keys are value names, values are ids of tags to update
                url: hideSubmitUrlSelector,
                option: hideSubmitOptionSelector,
                title: "#id--hide-modal-heading",
                type: "#id--hide-modal-element",
                action: "#id--hide-modal-action",
                submit: "#id--submit-btn-hide-modal",
            });
        });
    }
}

$(document).ready(function () {
    // set click handlers for reactions
    setReactionHandlers();
});
