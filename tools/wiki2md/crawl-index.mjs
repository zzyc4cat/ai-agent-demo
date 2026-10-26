// 抓取索引页里的链接（只保留 /zh/x1/troubleshooting/ 下的非 HMS 页）
import { chromium } from 'playwright';

const url = process.argv[2];
if (!url) { console.error('usage: node crawl-index.mjs <url>'); process.exit(2); }

const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(3000);

const links = await page.evaluate(() => {
  const self = location.href.replace(/\/$/, '');
  const seen = new Set();
  const out = [];
  for (const a of document.querySelectorAll('a[href]')) {
    const href = a.href.split('#')[0].replace(/\/$/, '');
    if (!/\/zh\/x1\/troubleshooting\//i.test(href)) continue;
    if (/\/hmscode\/|intro-hms|\/hms\/home/i.test(href)) continue;
    if (href === self) continue;
    if (seen.has(href)) continue;
    seen.add(href);
    out.push({ href, text: (a.textContent || '').replace(/\s+/g, ' ').trim() });
  }
  return out;
});

console.log(JSON.stringify(links, null, 2));
await browser.close();
