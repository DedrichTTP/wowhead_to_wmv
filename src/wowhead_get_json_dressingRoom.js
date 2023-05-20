const puppeteer = require('puppeteer-extra');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
const fs = require('fs');
const path = require('path');
const { exit } = require('process');

puppeteer.use(AdblockerPlugin());
const fetchUrl = async(urlInput, saveDir) => {
  try {
    console.log("Loading URL...")
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

        await page.goto(urlInput);

        // Extract the last arguments passed to `console.log`
        console.log("Waiting for model information... (Max 30s)")
        try {
          await page.waitForFunction(
              'window.lastLogArgs !== undefined'
          );
          const logArgs = await page.evaluate(() => window.lastLogArgs); 
          const viewerOptions = logArgs[1]; // The object `t` is the second argument
        } catch (error) {
          console.error("Error Timeout: The model took too long to load");
        }

        // Save the viewerOptions object as a JSON file
        // Save the JSON data to the specified directory
        const savePath = `${saveDir}/data.json`;
        fs.writeFileSync(savePath, JSON.stringify(viewerOptions, null, 2));

        await browser.close();
    } catch (error) {
        console.error("An error occurred:");
        console.log(error)
        console.log("exiting...")
        exit()
    }
}

const urlInput = process.argv[2];
const saveDir = process.argv[3];

if (!urlInput || !saveDir) {
  console.error("Please provide a URL and a save directory");
} else {
  fetchUrl(urlInput, saveDir);
}
