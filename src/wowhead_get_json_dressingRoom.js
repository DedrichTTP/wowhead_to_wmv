const puppeteer = require("puppeteer-extra");
const AdblockerPlugin = require("puppeteer-extra-plugin-adblocker");
const fs = require("fs");
const path = require("path");
const { exit } = require("process");
const https = require("https");

puppeteer.use(AdblockerPlugin());
const fetchUrl = async (urlInput, saveDir) => {
  try {
    // Check if the URL is valid
    const urlRegex = /^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/gm;
    if (!urlRegex.test(urlInput)) {
      console.error("Please provide a valid URL");
      return;
    }

    // Check if the save directory already exists
    if (!fs.existsSync(saveDir)) {
      fs.mkdirSync(saveDir);
    }

    console.log("Loading URL...");

    const browser = await puppeteer.launch({
      headless: "new",
      args: ["--disable-cache", "--disable-application-cache"],
    });
    const page = await browser.newPage();

    // Set request interception to true
    await page.setRequestInterception(true);

    // Download png files
    page.on("request", async (interceptedRequest) => {
      const url = interceptedRequest.url();
      // console.log(url)
      // Check if the request is for a .png file from the target URL
      if (
        url.startsWith("https://wow.zamimg.com/modelviewer/live/textures/") &&
        path.extname(url) === ".png" || path.extname(url) === ".webp"
      ) {
        // Download and save the .png file
        fs.mkdirSync(`${saveDir}/images`, { recursive: true });
        const file = fs.createWriteStream(
          `${saveDir}/images/${path.basename(url)}`
        );
        const request = https.get(url, function (response) {
          response.pipe(file);
        });
      }
      interceptedRequest.continue();
    });

    // Overwrite the `console.log` function on the page
    await page.evaluateOnNewDocument(() => {
      console.log = (function (originalLog) {
        return function () {
          if (
            arguments.length &&
            typeof arguments[0] === "string" &&
            arguments[0].startsWith("Creating viewer with options")
          ) {
            window.lastLogArgs = arguments;
          }
          originalLog.apply(console, arguments);
        };
      })(console.log);
    });

    await page.goto(urlInput);

    // Extract the last arguments passed to `console.log`
    console.log("Waiting for model information... (Max 30s)");
    try {
      await page.waitForFunction("window.lastLogArgs !== undefined");
      const logArgs = await page.evaluate(() => window.lastLogArgs);
      viewerOptions = logArgs[1]; // The object `t` is the second argument
      // console.log(viewerOptions)
    } catch (error) {
      console.error("Error Timeout: The model took too long to load");
    }

    // Save the viewerOptions object as a JSON file
    // Save the JSON data to the specified directory
    const savePath = `${saveDir}/data.json`;
    fs.writeFileSync(savePath, JSON.stringify(viewerOptions, null, 2));

    // Check if the file was successfully written before exiting
    if (fs.existsSync(savePath)) {
      console.log("Successfully saved the file!");
    } else {
      console.error("Failed to save the file!");
    }

    await browser.close();
  } catch (error) {
    console.error("An error occurred:");
    console.log(error);
    console.log("exiting...");
    exit();
  }
  return "Success";
};

const urlInput = process.argv[2];
const saveDir = process.argv[3];
console.log(saveDir)
if (!urlInput || !saveDir) {
  console.error("Please provide a URL and a save directory");
} else {
  fetchUrl(urlInput, saveDir);
}