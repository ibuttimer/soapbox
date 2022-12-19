/**
 * Jest puppeteer environment script adapted from
 * https://jestjs.io/docs/puppeteer#custom-example-without-jest-puppeteer-preset
 */

const {readFile} = require('fs').promises;
const os = require('os');
const path = require('path');
const puppeteer = require('puppeteer');
const NodeEnvironment = require('jest-environment-node').TestEnvironment;
const config = require('./test_config.json');

const DIR = path.join(os.tmpdir(), 'jest_puppeteer_global_setup');

class PuppeteerEnvironment extends NodeEnvironment {
    constructor(config) {
        super(config);
    }

    async setup() {
        await super.setup();
        // get the wsEndpoint
        const wsEndpoint = await readFile(path.join(DIR, 'wsEndpoint'), 'utf8');
        if (!wsEndpoint) {
            throw new Error('wsEndpoint not found');
        }

        // connect to puppeteer
        this.global.__BROWSER_GLOBAL__ = await puppeteer.connect({
            browserWSEndpoint: wsEndpoint,
        });

        // copy test data to global
        for (const [key, value] of Object.entries(config)) {
            this.global[key.toUpperCase()] = value;
        }
    }

    async teardown() {
        await super.teardown();
    }

    getVmContext() {
        return super.getVmContext();
    }
}

module.exports = PuppeteerEnvironment;
