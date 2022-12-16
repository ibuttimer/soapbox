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
 * Node.js script to scrape project artifacts.
 *
 * Options:
 *       --version                Show version number                     [boolean]
 *   -p, --password               Password to use                          [string]
 *   -t, --testpath               Test folder *relative to project root*
 *                                                   [string] [default: "doc/test"]
 *   -o, --htmlpath               Folder to save html files
 *                                                  [string] [default: "generated"]
 *   -v, --view                   View/view group to scrape
 *                                                        [string] [default: "all"]
 *   -s, --show                   Show pages in browser, i.e. non-headless mode
 *                                                       [boolean] [default: false]
 *   -l, --list                   List view/view group options
 *                                                       [boolean] [default: false]
 *       --id_opinion, --io       Id of opinion               [number] [default: 0]
 *       --id_comment, --ic       Id of comment               [number] [default: 0]
 *       --pending_opinion, --po  Id of opinion pending review[number] [default: 0]
 *       --under_opinion, --uo    Id of opinion under review  [number] [default: 0]
 *       --fail_opinion, --fo     Id of unacceptable content opinion
 *                                                            [number] [default: 0]
 *       --pending_comment, --pc  Id of comment pending review[number] [default: 0]
 *       --under_comment, --uc    Id of comment under review  [number] [default: 0]
 *       --fail_comment, --fc     Id of unacceptable comment opinion
 *                                                            [number] [default: 0]
 *       --help                   Show help                               [boolean]
 */
import puppeteer from 'puppeteer';
import esMain from 'es-main';
import yargs from 'yargs/yargs'
import { hideBin } from 'yargs/helpers'
import path from 'path';
import fs from 'fs';
import {
    loginUrl,
    logoutUrl,
    views,
    allViews,
    pre_login_views,
    preLoginViews,
    post_login_views,
    postLoginViews,
    moderator_views,
    moderatorViews,
    usernameTag,
    listViews,
    modOpinionReviewPreAssignView,
    opinionPreIdTag,
    modOpinionReviewPostAssignView,
    opinionPostIdTag,
    modOpinionReviewUnacceptableView,
    opinionNgIdTag,
    modCommentReviewPreAssignView,
    commentPreIdTag,
    modCommentReviewPostAssignView,
    commentPostIdTag,
    modCommentReviewUnacceptableView, commentNgIdTag, opinionIdTag, commentIdTag
} from './views.js'
import {login, logout, defaultUrl, defaultTestPath} from './lighthouse.js';

const defaultHtmlPath = 'generated';
const rootPath = path.dirname(process.cwd());

/**
 * Parse arguments
 * @returns {*}
 */
function parseArgs() {
    return yargs(hideBin(process.argv))
        .option('baseurl', {
            alias: 'b',
            type: 'string',
            description: 'Base url of site to scrape',
            default: defaultUrl
        })
        .option('username', {
            alias: 'u',
            type: 'string',
            description: 'Username to use'
        })
        .option('password', {
            alias: 'p',
            type: 'string',
            description: 'Password to use'
        })
        .option('testpath', {
            alias: 't',
            type: 'string',
            description: 'Test folder *relative to project root*',
            default: defaultTestPath
        })
        .option('htmlpath', {
            alias: 'o',
            type: 'string',
            description: 'Folder to save html files',
            default: defaultHtmlPath
        })
        .option('view', {
            alias: 'v',
            type: 'string',
            description: 'View/view group to scrape',
            default: allViews
        })
        .option('show', {
            alias: 's',
            type: 'boolean',
            description: 'Show pages in browser, i.e. non-headless mode',
            default: false
        })
        .option('list', {
            alias: 'l',
            type: 'boolean',
            description: 'List view/view group options',
            default: false
        })
        .option('id_opinion', {
            alias: 'io',
            type: 'number',
            description: 'Id of opinion',
            default: 0
        })
        .option('id_comment', {
            alias: 'ic',
            type: 'number',
            description: 'Id of comment',
            default: 0
        })
        .option('pending_opinion', {
            alias: 'po',
            type: 'number',
            description: 'Id of opinion pending review',
            default: 0
        })
        .option('under_opinion', {
            alias: 'uo',
            type: 'number',
            description: 'Id of opinion under review',
            default: 0
        })
        .option('fail_opinion', {
            alias: 'fo',
            type: 'number',
            description: 'Id of unacceptable content opinion',
            default: 0
        })
        .option('pending_comment', {
            alias: 'pc',
            type: 'number',
            description: 'Id of comment pending review',
            default: 0
        })
        .option('under_comment', {
            alias: 'uc',
            type: 'number',
            description: 'Id of comment under review',
            default: 0
        })
        .option('fail_comment', {
            alias: 'fc',
            type: 'number',
            description: 'Id of unacceptable comment opinion',
            default: 0
        })
        .help()
        .parse()
}
async function scape() {
    const argv = parseArgs();

    if (argv.list) {
        listViews();
        process.exit();
    }

    await puppeteer
        .launch({
            headless: !argv.show,    // Optional, if you want to see the tests in action.
        })
        .then(async (browser) => {

            const page = await browser.newPage();

            let viewList
            const target = argv.view.toLowerCase();
            if (target === allViews) {
                viewList = views;
            } else if (target === preLoginViews) {
                viewList = pre_login_views;
            } else if (target === postLoginViews) {
                viewList = post_login_views;
            } else if (target === moderatorViews) {
                viewList = moderator_views;
            } else {
                viewList = views.filter(entry => entry.name === target);
            }

            let isLoggedIn = false;
            for (const view of viewList) {

                let name = view.name;
                if (view.login) {
                    if (!isLoggedIn) {
                        // setup the browser session to be logged into site.
                        await login(browser, loginUrl, argv);
                        isLoggedIn = true;
                    }
                } else {
                    if (isLoggedIn) {
                        // setup the browser session to be logged out of site.
                        await logout(browser, logoutUrl, argv);
                        isLoggedIn = false;
                    }
                }

                let url = path.join(view.path);

                for (const keyVal of [
                    [usernameTag, argv.username],
                    [opinionIdTag, argv.id_opinion],
                    [commentIdTag, argv.id_comment],
                    [opinionPreIdTag, argv.pending_opinion],
                    [opinionPostIdTag, argv.under_opinion],
                    [opinionNgIdTag, argv.fail_opinion],
                    [commentPreIdTag, argv.pending_comment],
                    [commentPostIdTag, argv.under_comment],
                    [commentNgIdTag, argv.fail_comment],
                ]) {
                    if (url.indexOf(keyVal[0]) >= 0) {
                        url = url.replace(keyVal[0], keyVal[1]);
                    }
                }
                url = new URL(url, argv.baseurl);

                console.log(`Scraping ${url}: ${view.name}`);

                await page.goto(url, {
                    waitUntil: "load",
                    timeout: 0,
                });

                const html = await page.content();

                const htmlFile = path.join(rootPath, argv.testpath, argv.htmlpath, `${name}.html`)
                // save the scraped html
                fs.writeFileSync(htmlFile, html, err => {});
            }

            await browser.close();
        });
}

if (esMain(import.meta)) {
    scape().then();
}
