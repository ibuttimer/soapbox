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

const {getByTestId, screen} = require('@testing-library/dom');
require('@testing-library/jest-dom');
require('@testing-library/jest-dom/extend-expect');
require('@testing-library/jest-dom/matchers');
const path = require('path');


const timeout = 10000;
const usernameSelector = '#id_login';
const passwordSelector = '#id_password';
const signInSelector = '#id--sign-in';
const signOutSelector = '#id--sign-out';
const reactionsSelectedClass = "reactions-selected";

describe(
    'Login Page',
    () => {
        let page;
        beforeAll(async () => {
            page = await globalThis.__BROWSER_GLOBAL__.newPage();
            await page.goto(globalThis.HOST_URL);
        }, timeout);

        it('Landing should be titled "SoapBox"', async () => {
            await expect(page.title()).resolves.toMatch('SoapBox');
        });

        it('Landing should load without error', async () => {
            let element = await page.$("#id--sign-in");
            await expect((await element.getProperty("innerText")).jsonValue()).resolves.toMatch('Sign In');
            await element.dispose();

            element = await page.$("#id--register");
            await expect((await element.getProperty("innerText")).jsonValue()).resolves.toMatch('Register');
            await element.dispose();
        });

        it('Sign In should be titled "Sign In"', async () => {
            const url = path.join(globalThis.HOST_URL, '/accounts/login/');
            await page.goto(url);
            await expect(page.title()).resolves.toMatch('Sign In');
        }, timeout);

        it('Sign In should login', async () => {
            for (const selector of [
                usernameSelector, passwordSelector, signInSelector
            ]) {
                const element = await page.$(selector);
                await expect(element !== null).toBeTruthy();
                await element.dispose();
            }

            // https://devdocs.io/puppeteer/index#pagetypeselector-text-options
            await page.type(usernameSelector, globalThis.USERNAME, {delay: 100}); // Types slower, like a user
            await page.type(passwordSelector, globalThis.PASSWORD, {delay: 100}); // Types slower, like a user

            // https://devdocs.io/puppeteer/index#pageclickselector-options
            // need to wait for click & navigation together to avoid possible race condition
            await Promise.all([
                page.waitForNavigation({timeout: timeout}),
                page.click(signInSelector),
            ]);

            const bodyHandle = await page.$('body');
            await expect(page.evaluate(body => body.innerHTML, bodyHandle)).resolves.toMatch(`Successfully signed in as ${globalThis.USERNAME}`);
            await bodyHandle.dispose();
        }, timeout);

        it('Should display opinion', async () => {
            const url = path.join(globalThis.HOST_URL, `/opinions/${globalThis.OPINION_ID}/?mode=read-only`);
            await page.goto(url);

            const bodyHandle = await page.$('body');
            let html = await bodyHtml();
            await expect(page.evaluate(body => body.innerHTML, bodyHandle)).resolves.toMatch(globalThis.OPINION_TITLE);
            await bodyHandle.dispose();
        }, timeout);

        async function tagInnerHtml(selector) {
            const handle = await page.$(selector);
            const html = await page.evaluate(element => element.innerHTML, handle);
            await handle.dispose();
            return html;
        }
        async function bodyHtml() {
            return await tagInnerHtml('body');
        }

        const getElementAttribute = (elementId, attribute) => {
            const element = document.getElementById(elementId);
            return element.getAttribute(attribute);
        };

        const getElementClass = (elementId) => {
            return getElementAttribute(elementId, 'class');
        };

        const getElementOuterHtml = (elementId) => {
            const element = document.getElementById(elementId);
            return element.outerText;
        };

        const getElementInnerHtml = (elementId) => {
            const element = document.getElementById(elementId);
            return element.innerHTML;
        };

        const reactIds = (opinion_id) => {
            return {
                // agree/disagree buttons
                agreeId: `id--react-agree-opinion-${opinion_id}`,
                disagreeId: `id--react-disagree-opinion-${opinion_id}`,
                // follow/unfollow list items
                followLiId: `id--react-li-follow-opinion-${opinion_id}`,
                unfollowLiId: `id--react-li-unfollow-opinion-${opinion_id}`,
                // follow/unfollow buttons
                followId: `id--react-follow-opinion-${opinion_id}`,
                unfollowId: `id--react-unfollow-opinion-${opinion_id}`,
            }
        }

        async function clickAndWait(selector) {
            await Promise.all( [
                page.click(selector),
                page.waitForResponse( response => response.status() === 200 ),
            ]);
        }

        async function clickAndGetClass(elementId) {
            await clickAndWait(`#${elementId}`);
            return page.evaluate(getElementClass, elementId);
        }

        it.skip('Toggle opinion agree', async () => {
            // toggle the agree button and, it's class attribute should update to have/not have 'reactions-selected'
            const ids = reactIds(globalThis.OPINION_ID);

            let html = await clickAndGetClass(ids.agreeId)
            let isSelected = html.includes(reactionsSelectedClass);
            const expected = !isSelected;

            html = await clickAndGetClass(ids.agreeId)
            isSelected = html.includes(reactionsSelectedClass);
            await expect(isSelected === expected).toBeTruthy();
        }, timeout);

        it.skip('Change opinion agree to disagree', async () => {
            // select the disagree button and the class attribute 'reactions-selected' should move from agree to disagree button
            const ids = reactIds(globalThis.OPINION_ID);

            let html = await page.evaluate(getElementClass, ids.agreeId);
            let isSelected = html.includes(reactionsSelectedClass);

            if (!isSelected) {
                // select agree to give it 'reactions-selected'
                html = await clickAndGetClass(ids.agreeId)
                await expect(html.includes(reactionsSelectedClass)).toBeTruthy();
            }

            // disagree should have 'reactions-selected'
            await clickAndWait(`#${ids.disagreeId}`);
            html = await page.evaluate(getElementClass, ids.disagreeId);
            isSelected = html.includes(reactionsSelectedClass);
            await expect(isSelected).toBeTruthy();

            // agree should not have 'reactions-selected'
            html = await page.evaluate(getElementClass, ids.agreeId);
            isSelected = html.includes(reactionsSelectedClass);
            await expect(isSelected).toBeFalsy();
        }, timeout);

        it('Toggle author follow/unfollow', async () => {
            // select the follow button and the unfollow list item will be empty and visa-versa
            const ids = reactIds(globalThis.OPINION_ID);

            let html = await page.evaluate(getElementInnerHtml, ids.followLiId);
            let notFollowing = html.includes(ids.followId);  // not following if follow is available
            html = await page.evaluate(getElementInnerHtml, ids.unfollowLiId);
            let following = html.includes(ids.unfollowId);  // following if unfollow is available
            await expect(following === notFollowing).toBeFalsy();

            html = await bodyHtml();
            let clickId;    // button to click to toggle
            if (following) {
                clickId = ids.unfollowId;
            } else {
                clickId = ids.followId;
            }
            await clickAndWait(`#${clickId}`);

            html = await page.evaluate(getElementInnerHtml, ids.followLiId);
            notFollowing = html.includes(ids.followId);  // not following if follow is available
            await expect(following === notFollowing).toBeTruthy();   // following should not be equal to the old not following
            html = await page.evaluate(getElementInnerHtml, ids.unfollowLiId);
            following = html.includes(ids.unfollowId);  // following if unfollow is available
            await expect(following === notFollowing).toBeFalsy();
        }, timeout);

        it('should logout', async () => {
            const url = path.join(globalThis.HOST_URL, '/accounts/logout/');

            await page.goto(url);

            // const bodyHandle = await page.$('body');
            // const html = await page.evaluate(body => body.innerHTML, bodyHandle);

            // https://devdocs.io/puppeteer/index#pageclickselector-options
            // need to wait for click & navigation together to avoid possible race condition
            await Promise.all([
                page.waitForNavigation({timeout: timeout}),
                page.click(signOutSelector),
            ]);

            const bodyHandle = await page.$('body');
            await expect(page.evaluate(body => body.innerHTML, bodyHandle)).resolves.toMatch(`You have signed out`);
            await bodyHandle.dispose();

        }, timeout);
    },
    timeout,
);
