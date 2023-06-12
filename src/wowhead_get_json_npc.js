const puppeteer = require("puppeteer");
const fs = require("fs");
const axios = require("axios");

// Get the wowhead JSON file for the given URL
const fetchUrl = async (urlInput, saveDir) => {
  console.log("Loading URL...");
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  let interceptedUrl = ""; // Variable to store the intercepted URL

  // Begin intercepting requests before navigating to the URL
  await page.setRequestInterception(true);
  console.log("Waiting for model information... (Max 30s)");
  page.on("request", (interceptedRequest) => {
    if (interceptedUrl) {
      interceptedRequest.abort();
      return;
    }

    const url = interceptedRequest.url();

    // If the request is for the target JSON file, save it
    if (url.startsWith("https://wow.zamimg.com/modelviewer/live/meta/npc")) {
      interceptedUrl = url;
    }

    interceptedRequest.continue();
  });

  await page.goto(urlInput);
  await browser.close();

  if (!interceptedUrl) {
    console.error("No JSON file was intercepted");
    return;
  }

  // Fetch JSON data from the intercepted URL
  const response = await axios.get(interceptedUrl);
  const jsonData = response.data;

  // Save the JSON data to the specified directory
  const savePath = `${saveDir}/data.json`;
  fs.writeFileSync(savePath, JSON.stringify(jsonData, null, 2));
};

const urlInput = process.argv[2];
const saveDir = process.argv[3];

if (!urlInput || !saveDir) {
  console.error("Please provide a URL and a save directory");
} else {
  fetchUrl(urlInput, saveDir);
}