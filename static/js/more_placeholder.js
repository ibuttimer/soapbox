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

// More placeholder buttons are named 'id--comment-more-placeholder-<id>'
const MORE_PLACEHOLDER_SELECTOR = "button[id^='id--comment-more-placeholder']";
// Comment collapse divs are named 'id--comment-collapse-<id>'
const COMMENT_COLLAPSE_SELECTOR = "div[id^='id--comment-collapse']"
// Comment collapse toggle links are named 'id--comment-collapse-<id>-toggle'
const COMMENT_COLLAPSE_TOGGLE_SELECTOR = "a[id^='id--comment-collapse'][id$='toggle']";

const DATA_COMMENT_QUERY = 'data-comment-query';

/* Click handler for more comments placeholder */
function morePlaceholderClickHandler(event) {
    const url = `${event.currentTarget.attributes['data-bs-href'].textContent}&ref=${window.location.pathname}`;

    // hide tooltip
    $("#" + event.currentTarget.id).tooltip("hide");

    $.ajax({
        method: 'get',
        url: url,
    }).done(function (data) {
        // remove placeholder click handlers
        $(MORE_PLACEHOLDER_SELECTOR).off();

        // comment card more div has id "id--comment-card-more-<id>"
        const splits = event.currentTarget.id.split('-');
        const commentId = splits[splits.length - 1]
        const moreDivIdSelector = `#id--comment-card-more-${commentId}`;
        // add additional comments to end of list
        $(moreDivIdSelector).parent().append(data.html);
        // remove more placeholder & collapse
        $(moreDivIdSelector).remove();
        $(`#id--comment-collapse-more-${commentId}`).remove();
        // remove any (on whatever level) dynamically inserted elements that are displaying out of place
        $(".dynamic-insert-remove").remove();

        // set placeholder click handlers
        addMorePlaceholderHandlers();
        // set click handlers for reactions
        setReactionHandlers();
        enableTooltips();
    });
}

/* Click handler for sub-level comments */
function subLevelCommentsClickHandler(event) {
    if (event.currentTarget.hasAttribute(DATA_COMMENT_QUERY)) {
        const query = event.currentTarget.attributes[DATA_COMMENT_QUERY].textContent;

        const url = `${COMMENT_MORE_URL}?${query}&ref=${window.location.pathname}`;

        $.ajax({
            method: 'get',
            url: url,
        }).done(function (data) {

            // Comment collapse toggle links are named 'id--comment-collapse-<id>-toggle'
            const splits = event.currentTarget.id.split('-');
            const commentId = splits[splits.length - 2]
            const collapseDivIdSelector = "#id--comment-collapse-" + commentId;

            // add additional comments to end of list
            $(collapseDivIdSelector).append(data.html);
            // remove comment query from collapse toggle
            event.currentTarget.removeAttribute(DATA_COMMENT_QUERY);

            // set click handlers for reactions
            setReactionHandlers();
            enableTooltips();
            // add sub-level comment handlers
            addSubLevelHandlers();
        });
    }
}

function setCollapseDisplayHandlers() {
    // remove old handlers to prevent duplicates
    $(COMMENT_COLLAPSE_SELECTOR).off();

    for (const type of ['hidden.bs.collapse', 'shown.bs.collapse']) {
        $(COMMENT_COLLAPSE_SELECTOR).on(type, updateCollapseDisplay);
    }
}


const toggleSpanSelector = (event) => "#" + event.currentTarget.id + "-toggle > i";

/* Event handler to update collapse toggle display */
function updateCollapseDisplay(event) {
    const selector = toggleSpanSelector(event)
    // default shown event
    let toRemove = "fa-chevron-down";
    let toAdd = "fa-chevron-up";
    if (event.type === 'hidden') {
        toRemove = "fa-chevron-up";
        toAdd = "fa-chevron-down";
    }
    $(selector).removeClass(toRemove);
    $(selector).addClass(toAdd);
    // prevent propagation back up to the parent tags to stop them changing as well
    event.stopPropagation();
}

/* Add handlers to request more comments */
function addMorePlaceholderHandlers() {
    /* Click handler to request more comments */
    $(MORE_PLACEHOLDER_SELECTOR).on('click', morePlaceholderClickHandler);
}

/* Add handlers to display/request sub-level comments */
function addSubLevelHandlers() {
    /* Add collapse event handlers for comment reply containers */
    setCollapseDisplayHandlers();
    /* Event handlers for sub-level comments containers */
    $(COMMENT_COLLAPSE_TOGGLE_SELECTOR).on('click', subLevelCommentsClickHandler);
}

$(document).ready(function () {

    /* Handler for request more comments */
    addMorePlaceholderHandlers();
    /* Handlers for sub-level comments */
    addSubLevelHandlers();
});
