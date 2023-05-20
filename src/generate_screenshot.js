const puppeteer = require('puppeteer-extra');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
puppeteer.use(AdblockerPlugin());

async function takeScreenshot(url, imagePath) {
    const browser = await puppeteer.launch({headless: "new"});
    const page = await browser.newPage();
    await page.goto(url);
    await page.waitForSelector('#paperdoll-model-dressing-room-paperdoll');

    // Edit the page before-hand
    await page.evaluate(() => {
       let el = document.querySelector('#dressing-room > div.dressing-room-character');
    if (el) {
        el.setAttribute('data-hide-ui', 'true');
    }

    let elToRemove = document.querySelector('body > div.notifications-dialog');
    if (elToRemove) elToRemove.parentNode.removeChild(elToRemove);
    });

    // Add a delay before taking screenshot
    await new Promise(r => setTimeout(r, 3500));

    const element = await page.$('#paperdoll-model-dressing-room-paperdoll');
    await element.screenshot({ path: imagePath, type: 'jpeg', quality: 90 });

    await browser.close();
}

const url = process.argv[2];
const imagePath = process.argv[3];

takeScreenshot(url, imagePath);
