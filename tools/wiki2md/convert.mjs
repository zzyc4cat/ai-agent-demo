// wiki2md: 用本机 Edge 渲染 SPA 页面，抽取正文并转成 Markdown。
// 用法: node convert.mjs <url> <out.md>
import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';
import { dirname } from 'path';

const [, , url, out] = process.argv;
if (!url || !out) {
  console.error('usage: node convert.mjs <url> <out.md>');
  process.exit(2);
}

const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
try {
  await page.waitForSelector('article, .theme-default-content, .vp-doc, main', { timeout: 15000 });
} catch {}
await page.waitForTimeout(2500);

const result = await page.evaluate(() => {
  const root =
    document.querySelector('article') ||
    document.querySelector('.theme-default-content') ||
    document.querySelector('.vp-doc') ||
    document.querySelector('main') ||
    document.body;

  const abs = (u) => {
    try { return new URL(u, location.href).href; } catch { return u; }
  };
  const clean = (s) => s.replace(/\s+/g, ' ').trim();
  const SKIP = new Set(['script', 'style', 'nav', 'footer', 'header', 'aside', 'button', 'form']);

  const media = [];
  const skipMedia = (u) => /consent|trustarc|cookie|logo|icon|sprite/i.test(u || '');
  root.querySelectorAll('video, iframe').forEach((el) => {
    const src = el.getAttribute('src') ||
      el.querySelector('source')?.getAttribute('src') ||
      el.getAttribute('data-src');
    if (src && !skipMedia(src)) media.push({ kind: el.tagName.toLowerCase(), url: abs(src) });
  });
  root.querySelectorAll('img').forEach((img) => {
    const src = img.getAttribute('src') || img.getAttribute('data-src');
    if (src && !src.startsWith('data:') && !skipMedia(src)) media.push({ kind: 'img', url: abs(src) });
  });

  function inline(node) {
    let out = '';
    for (const n of node.childNodes) {
      if (n.nodeType === 3) { out += n.textContent; continue; }
      if (n.nodeType !== 1) continue;
      const tag = n.tagName.toLowerCase();
      if (tag === 'a') out += `[${clean(n.textContent)}](${abs(n.getAttribute('href') || '')})`;
      else if (tag === 'code') out += '`' + n.textContent + '`';
      else if (tag === 'img') out += `![${n.getAttribute('alt') || ''}](${abs(n.getAttribute('src') || '')})`;
      else if (tag === 'br') out += '\n';
      else if (tag === 'strong' || tag === 'b') out += `**${clean(n.textContent)}**`;
      else out += inline(n);
    }
    return out;
  }

  function block(node, depth = 0) {
    let out = '';
    for (const n of node.childNodes) {
      if (n.nodeType === 3) { const t = clean(n.textContent); if (t) out += t + '\n'; continue; }
      if (n.nodeType !== 1) continue;
      const tag = n.tagName.toLowerCase();
      if (SKIP.has(tag)) continue;
      if (/^h[1-6]$/.test(tag)) { out += '\n' + '#'.repeat(+tag[1]) + ' ' + clean(n.textContent) + '\n\n'; continue; }
      if (tag === 'p') { const t = inline(n).trim(); if (t) out += t + '\n\n'; continue; }
      if (tag === 'ul' || tag === 'ol') {
        let i = 1;
        for (const li of n.querySelectorAll(':scope > li')) {
          const marker = tag === 'ol' ? `${i++}. ` : '- ';
          out += '  '.repeat(depth) + marker + inline(li).trim() + '\n';
        }
        out += '\n';
        continue;
      }
      if (tag === 'table') {
        const rows = [...n.querySelectorAll('tr')];
        if (!rows.length) continue;
        const cells = (tr) => [...tr.querySelectorAll('th,td')].map((c) => clean(c.textContent).replace(/\|/g, '\\|'));
        const head = cells(rows[0]);
        out += '| ' + head.join(' | ') + ' |\n';
        out += '| ' + head.map(() => '---').join(' | ') + ' |\n';
        for (const tr of rows.slice(1)) out += '| ' + cells(tr).join(' | ') + ' |\n';
        out += '\n';
        continue;
      }
      if (tag === 'pre') { out += '\n```\n' + n.textContent.trim() + '\n```\n\n'; continue; }
      if (tag === 'blockquote') {
        const t = inline(n).trim();
        out += t.split('\n').map((l) => '> ' + l).join('\n') + '\n\n';
        continue;
      }
      if (tag === 'img') { out += `![${n.getAttribute('alt') || ''}](${abs(n.getAttribute('src') || '')})\n\n`; continue; }
      if (tag === 'hr') { out += '\n---\n\n'; continue; }
      out += block(n, depth);
    }
    return out;
  }

  const pageTitle = (document.title || '').replace(/\s*\|\s*Bambu Lab Wiki\s*$/, '').trim();
  const h1 = (document.querySelector('h1')?.textContent || '').replace(/¶/g, '').trim();
  return {
    title: pageTitle || h1,
    md: block(root),
    media,
  };
});

await browser.close();

// 清理：锚点符号、页面元信息块、评论区
let body = result.md.replace(/\n{3,}/g, '\n\n').trim();
body = body.replace(/¶\s*/g, '');
body = body.replace(/\n页面内容\n[\s\S]*?\n\d{2}\/\d{2}\/\d{4}\n/, '\n');
body = body.replace(/\n评论\n[\s\S]*$/, '\n');
body = body.replace(/\n#{1,6}\s*结束语[\s\S]*$/, '\n');
body = body.replace(/^---\n+/, '');

const today = new Date().toISOString().slice(0, 10);
const mediaLines = [...new Set(result.media.map((m) => `- ${m.kind}: ${m.url}`))];
const header = [
  '---',
  `source: ${url}`,
  `fetched_at: ${today}`,
  `title: ${result.title}`,
  `media_count: ${mediaLines.length}`,
  '---',
  '',
  `> 来源：${url}｜抓取日期：${today}｜仅供本地检索演示，版权归原作者`,
  '',
].join('\n');

const mediaSection = mediaLines.length
  ? `\n\n## 媒体资源\n\n${mediaLines.join('\n')}\n`
  : '';

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, header + '\n' + body + mediaSection + '\n', 'utf8');
console.log(`saved: ${out}`);
console.log(`chars: ${body.length}, media: ${mediaLines.length}`);
