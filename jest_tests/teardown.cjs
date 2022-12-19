/**
 * Jest global teardown script from
 * https://jestjs.io/docs/puppeteer#custom-example-without-jest-puppeteer-preset
 */

const fs = require('fs').promises;
const os = require('os');
const path = require('path');

const DIR = path.join(os.tmpdir(), 'jest_puppeteer_global_setup');
module.exports = async function () {
    // close the browser instance
    await globalThis.__BROWSER_GLOBAL__.close();

    // clean-up the wsEndpoint file
    await fs.rm(DIR, {recursive: true, force: true});
};
