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
 * Set focus when modal displayed
 * @param modalSelector: modal selector
 * @param focusTarget: focus target selector
 */
function modalFocus(modalSelector, focusTarget) {
    /* Due to how HTML5 defines its semantics, the autofocus HTML attribute has no effect in Bootstrap modals.
       To achieve the same effect, use some custom JavaScript
       https://getbootstrap.com/docs/5.2/components/modal/#how-it-works
     */
    $(modalSelector).on('shown.bs.modal', (event) => {
        $(focusTarget).focus();
    });
}

/**
 * Clear form errors and entered data when modal hidden
 * @param modalSelector: modal selector
 * @param errorsSelector: error container selector
 * @param inputSelector: input selector
 * @param isSummernote: is summernote input flag
 */
function resetModalForm(modalSelector, errorsSelector, inputSelector, isSummernote = false) {
    /* Clear form errors and entered data when modal hidden */
    $(modalSelector).on('hidden.bs.modal', (event) => {
        $(errorsSelector).html("");
        if (isSummernote) {
            /* TODO find method of clearing summernote editor content and remove all stored history
                suggested method (https://summernote.org/deep-dive/#reset) doesn't work (maybe because in iframe?)
                Can clear input element using $(inputSelector).val("") but editor content is still displayed
             */
        } else {
            $(inputSelector).val("")
        }
    });
}
