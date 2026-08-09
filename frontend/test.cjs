const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));
  await page.goto('http://localhost:5173');
  await page.waitForSelector('a[href="/login"]');
  console.log('Clicking login...');
  await page.click('a[href="/login"]');
  await new Promise(r => setTimeout(r, 2000));
  console.log('URL after click:', page.url());
  await browser.close();
})();
