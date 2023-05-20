const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const fetchUrl = async(urlInput, saveDir) => {
    const browser = await puppeteer.launch({headless: "new"});
    const page = await browser.newPage();

    // Overwrite the `console.log` function on the page
    await page.evaluateOnNewDocument(() => {
        console.log = (function(originalLog) {
            return function() {
                if (arguments.length &&
                    typeof arguments[0] === 'string' &&
                    arguments[0].startsWith('Creating viewer with options')) {
                    window.lastLogArgs = arguments;
                }
                originalLog.apply(console, arguments);
            };
        })(console.log);
    });

    console.log(`Going to page: ${urlInput}`)
    await page.goto(urlInput);

    // Extract the last arguments passed to `console.log`
    const logArgs = await page.evaluate(() => window.lastLogArgs);
    const viewerOptions = logArgs[1]; // The object `t` is the second argument

    // Save the viewerOptions object as a JSON file
    // Save the JSON data to the specified directory
    const savePath = `${saveDir}/data.json`;
    fs.writeFileSync(savePath, JSON.stringify(viewerOptions, null, 2));

    await browser.close();
}

const urlInput = process.argv[2];
const saveDir = process.argv[3];

if (!urlInput || !saveDir) {
  console.error("Please provide a URL and a save directory");
} else {
  fetchUrl(urlInput, saveDir);
}
