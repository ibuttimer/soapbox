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
 * Functions to support page content selection:
 * - sort_order_select.html
 * - per_page_pagination_select.html
 */

/**
 * Update sort order/per page
 * :param event: change event
 */
function update_content(order, per_page, page) {

    if (page === undefined) {
        page = "?page=1"
    }

    // remove per page and page handlers as new elements will be returned with the response
    $('#per-page-select').off();
    $('.page-item').off();

    const repeat_search = $('#var--repeat-search-term').text().trim();
    const query_args = [
        "order=" + order, "per-page=" + per_page, "reorder=1"
    ];
    if (repeat_search.length > 0) {
        query_args.push(repeat_search)
    }

    $.ajax({
        url: page + "&" + query_args.join("&")
    }).done(function(data) {
        $('#article-content').html(data);

        setReactionHandlers();
        enableTooltips();

        $('#per-page-select').ready(function(event) {
            add_page_content_handlers();
        });
    });
}

/** Get current per page value */
function get_per_page() {
    return $('#per-page-select').find(":selected").val();
}

/** Get current order value */
function get_order() {
    return $('#id--sort-order-select').find(":selected").val()
}

/** Get current page value */
function get_page() {
    const page = $('#current-page').find("a");
    return page.length ? "?page=" + page.text().trim() : undefined
}

/**
 * Add change handler for per page selector and pages
 */
function add_page_content_handlers() {
    /**
     * Change handler for per page
     * :param event: change event
     */
    $('#per-page-select').on( "change", function(event) {
        update_content(get_order(), event.target.value, get_page())
    });
    /**
     * Click handler for page request
     * :param event: change event
     */
    $('.page-item').on( "click", function(event) {
        event.preventDefault();
        update_content(get_order(), get_per_page(), event.currentTarget.firstElementChild.href)
    });
}


$(document).ready(function() {
    /**
     * Change handler for sort order
     * :param event: change event
     */
    $('#id--sort-order-select').on( "change", function(event) {
        update_content(event.target.value, get_per_page(), get_page())
    });

    add_page_content_handlers();
});
