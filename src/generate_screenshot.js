const puppeteer = require("puppeteer-extra");
const AdblockerPlugin = require("puppeteer-extra-plugin-adblocker");
puppeteer.use(AdblockerPlugin());

async function takeScreenshot(url, imagePath, characterType) {
  const browser = await puppeteer.launch({
    headless: "new",
    userDataDir: "./temp_profile",
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1920, height: 1080 });

  await page.goto(url);
  let element; // Define element variable here
  if (characterType == "custom") {
    // console.log("Custom")

    await page.waitForSelector("#paperdoll-model-dressing-room-paperdoll");
    // Edit the page before-hand
    await page.evaluate(() => {
      let el = document.querySelector(
        "#dressing-room > div.dressing-room-character"
      );
      if (el) {
        el.setAttribute("data-hide-ui", "true");
      }

      let elToRemove = document.querySelector(
        "body > div.notifications-dialog"
      );
      if (elToRemove) elToRemove.parentNode.removeChild(elToRemove);
    });

    element = await page.$("#paperdoll-model-dressing-room-paperdoll");
  } else {
    // console.log("NPC")

    await page.evaluate(() => {
      let el = document.querySelector("body > div.lightbox-outer > div > div");
      if (el) {
        el.style.padding = 0;
      }

      let elToRemove1 = document.querySelector(
        "body > div.lightbox-outer > div > div > div.lightbox-content.modelviewer-modelbg > div > a.fa.fa-arrows-alt"
      );
      if (elToRemove1) elToRemove1.parentNode.removeChild(elToRemove1);
      let elToRemove2 = document.querySelector(
        "body > div.lightbox-outer > div > div > div.lightbox-content.modelviewer-modelbg > div > a.fa.fa-pause"
      );
      if (elToRemove2) elToRemove2.parentNode.removeChild(elToRemove2);
    });

    element = await page.$(
      "body > div.lightbox-outer > div > div > div.lightbox-content.modelviewer-modelbg > div > canvas"
    );
  }

  await new Promise((r) => setTimeout(r, 3500));
  await element.screenshot({ path: imagePath, type: "jpeg", quality: 90 });
  await browser.close();
}

const url = process.argv[2];
const imagePath = process.argv[3];
const characterType = process.argv[4];

takeScreenshot(url, imagePath, characterType);
