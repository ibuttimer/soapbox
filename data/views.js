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
 * Node.js script of view configurations for 'lighthouse.js' and 'scrape.js'.
 */

export const loginUrl = '/accounts/login/';
export const logoutUrl = '/accounts/logout/';

/**
 * View config
 * @param {string} name - report name
 * @param {boolean} login - login required flag; true = needs to be logged in, false = does not need to be logged in
 * @param {string} path - relative path to generated file
 * @param {string} desc - description
 * @returns
 */
const viewCfg = (name, login, path, desc) => {
    return { name: name, login: login, path: path, desc: desc };
};
const validatorPath = 'val-test'
export const landingView = 'landing';
export const loginView = 'login';
export const signupView = 'signup';
export const socialLoginView = 'social-login';
export const logoutView = 'logout';
export const logoutValTestView = `${logoutView}-${validatorPath}`;
export const followingView = 'following';
export const followingValTest = `${followingView}-${validatorPath}`;
export const categoryView = 'category';
export const categoryViewValTest = `${categoryView}-${validatorPath}`;
export const opinionNewView = 'opinion-new';
export const opinionNewValTest = `${opinionNewView}-${validatorPath}`;
export const opinionReadView = 'opinion-read';
export const opinionReadValTest = `${opinionReadView}-${validatorPath}`;
export const opinionEditView = 'opinion-edit';
export const opinionEditValTest = `${opinionEditView}-${validatorPath}`;
export const opinionDraftView = 'opinion-draft';
export const opinionPreviewView = 'opinion-preview';
export const opinionsListDraftView = 'opinions-list-draft';
export const opinionsListPreviewView = 'opinions-list-preview';
export const opinionsListReviewView = 'opinions-list-review';
export const opinionsMineView = 'opinions-mine';
export const opinionsPinnedView = 'opinions-pinned';
export const opinionsFollowedNewView = 'opinions-follow-new';
export const opinionsFollowedAllView = 'opinions-follow-all';
export const opinionsAll = 'opinions-all';
export const opinionsAllValTest = `${opinionsAll}-${validatorPath}`;

export const commentsReviewView = 'comments-review';
export const commentsMineView = 'comments-mine';
export const commentsAll = 'comments-all';
export const commentsAllValTest = `${commentsAll}-${validatorPath}`;

export const modOpinionsPendingView = 'mod-opinions-pending';
export const modOpinionsPendingValTest = `${modOpinionsPendingView}-${validatorPath}`;

export const modOpinionsUnderView = 'mod-opinions-under';
export const modOpinionsUnacceptableView = 'mod-opinions-unacceptable';
export const modCommentsPendingView = 'mod-comments-pending';
export const modCommentsUnderView = 'mod-comments-under';
export const modCommentsUnacceptableView = 'mod-comments-unacceptable';
export const modOpinionReviewPreAssignView = 'mod-opinion-review-pre-assign';
export const modOpinionReviewPreAssignValTest = `${modOpinionReviewPreAssignView}-${validatorPath}`;
export const modOpinionReviewPostAssignView = 'mod-opinion-review-post-assign';
export const modOpinionReviewPostAssignValTest = `${modOpinionReviewPostAssignView}-${validatorPath}`;
export const modOpinionReviewUnacceptableView = 'mod-opinion-review-unacceptable';
export const modCommentReviewPreAssignView = 'mod-comment-review-pre-assign';
export const modCommentReviewPostAssignView = 'mod-comment-review-post-assign';
export const modCommentReviewUnacceptableView = 'mod-comment-review-unacceptable';

export const userProfileView = 'user-profile';
export const userProfileViewValTest = `${userProfileView}-${validatorPath}`;

export const preLoginViews = 'pre-login';
export const postLoginViews = 'post-login';
export const moderatorViews = 'moderator';
export const allViews = 'all';
export const usernameTag = '<username>'
export const opinionIdTag = '<opinion_id>'
export const commentIdTag = '<comment_id>'
export const opinionPreIdTag = '<opinion_pre_id>'
export const opinionPostIdTag = '<opinion_post_id>'
export const opinionNgIdTag = '<opinion_ua_id>'
export const commentPreIdTag = '<comment_pre_id>'
export const commentPostIdTag = '<comment_post_id>'
export const commentNgIdTag = '<comment_ua_id>'
/** List of all reports */
export const pre_login_views = [
    viewCfg(landingView, false, '/', 'landing view'),
    viewCfg(loginView, false, loginUrl, 'login view'),
    viewCfg(signupView, false, '/accounts/signup/', 'signup view'),
    viewCfg(socialLoginView, false, '/accounts/google/login/', 'social account login view'),
];
export const post_login_views = [
    viewCfg(followingView, true, '/feed/following/', 'following authors opinion feed'),
    viewCfg(followingValTest, true, `/feed/${validatorPath}/following/`, 'following authors opinion feed (validater path)'),
    viewCfg(categoryView, true, '/feed/category/', 'following categories opinion feed'),
    viewCfg(categoryViewValTest, true, `/feed/${validatorPath}/category/`, 'following categories opinion feed (validater path)'),

    viewCfg(opinionNewView, true, '/opinions/new/', 'create new opinion view'),
    viewCfg(opinionNewValTest, true, `/opinions/${validatorPath}/new/`, 'create new opinion view (validater path)'),
    viewCfg(opinionReadView, true, `/opinions/${opinionIdTag}/?mode=read-only`, 'opinion read view'),
    viewCfg(opinionReadValTest, true, `/opinions/${validatorPath}/${opinionIdTag}/?mode=read-only`, 'opinion read view (validater path)'),
    viewCfg(opinionEditView, true, `/opinions/${opinionIdTag}/?mode=edit`, 'edit opinion view'),
    viewCfg(opinionEditValTest, true, `/opinions/${validatorPath}/${opinionIdTag}/?mode=edit`, 'edit opinion view (validater path)'),
    viewCfg(opinionDraftView, true, `/opinions/${opinionIdTag}/?mode=read-only`, 'draft opinion readonly view'),
    viewCfg(opinionPreviewView, true, `/opinions/${opinionIdTag}/?mode=read-only`, 'preview opinion readonly view'),

    viewCfg(opinionsListDraftView, true, `/opinions/?author=${usernameTag}&status=draft`, "all user's draft opinions view" ),
    viewCfg(opinionsListPreviewView, true, `/opinions/?author=${usernameTag}&status=preview`, "all user's preview opinions view"),
    viewCfg(opinionsListReviewView, true, `/opinions/in_review/?author=${usernameTag}`, "all user's in review opinions view"),
    viewCfg(opinionsMineView, true, `/opinions/?author=${usernameTag}&status=all`, "all user's opinions view"),
    viewCfg(opinionsPinnedView, true, `/opinions/?pinned=yes`, "all user's pinned opinions view"),
    viewCfg(opinionsFollowedNewView, true, `/opinions/followed/?filter=new`, "all user's following authors new opinions since last login view"),
    viewCfg(opinionsFollowedAllView, true, `/opinions/followed/?filter=all`, "all user's following authors opinions login view"),
    viewCfg(opinionsAll, true, `/opinions/`, "all published opinions view"),
    viewCfg(opinionsAllValTest, true, `/opinions/${validatorPath}/`, "all published opinions view (validater path)"),

    viewCfg(commentsReviewView, true, `/opinions/comments/in_review/?author=${usernameTag}`, "all user's in review comments view"),
    viewCfg(commentsMineView, true, `/opinions/comments/?author=${usernameTag}&status=all`, "all user's comments view"),
    viewCfg(commentsAll, true, `/opinions/comments/`, "all comments view"),
    viewCfg(commentsAllValTest, true, `/opinions/${validatorPath}/comments/`, "all comments view (validater path)"),

    viewCfg(userProfileView, true, `/users/${usernameTag}/`, "user's profile view"),
    viewCfg(userProfileViewValTest, true, `/users/${validatorPath}/${usernameTag}/`, "user's profile view (validater path)"),
    viewCfg(logoutView, true, logoutUrl, 'logout view'),
    viewCfg(logoutValTestView, true, `/${validatorPath}/logout/`, 'logout view (validater path)'),
];
export const moderator_views = [
    viewCfg(modOpinionsPendingView, true, `/opinions/in_review/?review=pending-review`, "moderator's opinions pending review view"),
    viewCfg(modOpinionsPendingValTest, true, `/opinions/${validatorPath}/in_review/?review=pending-review`, "moderator's opinions pending review view (validater path)"),
    viewCfg(modOpinionsUnderView, true, `/opinions/in_review/?review=under-review`, "moderator's opinions under review view"),
    viewCfg(modOpinionsUnacceptableView, true, `/opinions/in_review/?review=unacceptable`, "moderator's opinions which failed review view"),
    viewCfg(modCommentsPendingView, true, `/opinions/comments/in_review/?review=pending-review`, "moderator's comments pending review view"),
    viewCfg(modCommentsUnderView, true, `/opinions/comments/in_review/?review=under-review`, "moderator's comments under review view"),
    viewCfg(modCommentsUnacceptableView, true, `/opinions/comments/in_review/?review=unacceptable`, "moderator's comments which failed review view"),

    viewCfg(modOpinionReviewPreAssignView, true, `/opinions/${opinionPreIdTag}/?mode=review`, "moderator's opinion pending review pre-assignment view"),
    viewCfg(modOpinionReviewPreAssignValTest, true, `/opinions/${validatorPath}/${opinionPreIdTag}/?mode=review`, "moderator's opinion pending review pre-assignment view (validater path)"),
    viewCfg(modOpinionReviewPostAssignView, true, `/opinions/${opinionPostIdTag}/?mode=review`, "moderator's opinion under review post-assignment view"),
    viewCfg(modOpinionReviewPostAssignValTest, true, `/opinions/${validatorPath}/${opinionPostIdTag}/?mode=review`, "moderator's opinion under review post-assignment view (validater path)"),
    viewCfg(modOpinionReviewUnacceptableView, true, `/opinions/${opinionNgIdTag}/?mode=review`, "moderator's opinion unacceptable view"),

    viewCfg(modCommentReviewPreAssignView, true, `/opinions/comments/${commentPreIdTag}/?mode=review`, "moderator's comment pending review pre-assignment view"),
    viewCfg(modCommentReviewPostAssignView, true, `/opinions/comments/${commentPostIdTag}/?mode=review`, "moderator's comment under review post-assignment view"),
    viewCfg(modCommentReviewUnacceptableView, true, `/opinions/comments/${commentNgIdTag}/?mode=review`, "moderator's comment unacceptable view"),
];
export const views = pre_login_views.concat(post_login_views).concat(moderator_views);

export function listViews() {
    const padString = str => `${str}${" ".repeat(35 - str.length)}`;

    console.log(`${padString(allViews)}: all views`)
    console.log(`${padString(preLoginViews)}: all pre-login views`)
    console.log(`${padString(postLoginViews)}: all post-login views`)
    console.log(`${padString(moderatorViews)}: all moderator views`)
    for (const view of views) {
        console.log(`${padString(view.name)}: ${view.desc}`)
    }
    process.exit();
}