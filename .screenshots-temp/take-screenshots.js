import puppeteer from 'puppeteer';
import { existsSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';

const root = resolve(process.cwd(), '..');
const [target, filter] = process.argv.slice(2);

function collect(dir, out) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      if (entry !== 'screenshots' && entry !== 'node_modules') collect(full, out);
    } else if (entry.endsWith('.html')) {
      out.push(full);
    }
  }
  return out;
}

function targets() {
  if (!target) {
    const files = [];
    for (const base of ['ProductSpecification/stories', 'ProductSpecification/stories/done']) {
      const abs = join(root, base);
      if (!existsSync(abs)) continue;
      for (const story of readdirSync(abs)) {
        const mock = join(abs, story, 'mockups');
        if (existsSync(mock)) collect(mock, files);
      }
    }
    return files;
  }
  const abs = resolve(process.cwd(), target);
  const files = statSync(abs).isDirectory() ? collect(abs, []) : [abs];
  return filter ? files.filter((f) => f.includes(filter)) : files;
}

function viewportFor(file) {
  return dirname(file).split('/').includes('mobile')
    ? { width: 390, height: 844, deviceScaleFactor: 2 }
    : { width: 1400, height: 900, deviceScaleFactor: 1 };
}

async function shoot(browser, file) {
  const page = await browser.newPage();
  await page.setViewport(viewportFor(file));
  await page.goto(`file://${file}`, { waitUntil: 'networkidle0', timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
  const outDir = join(dirname(file), 'screenshots');
  mkdirSync(outDir, { recursive: true });
  const path = join(outDir, basename(file, '.html') + '.png');
  const card = await page.$('.mockup-card');
  if (card) await card.screenshot({ path });
  else await page.screenshot({ path, fullPage: true });
  await page.close();
  return path;
}

const files = targets();
const browser = await puppeteer.launch({ headless: true });
let failed = 0;
for (const file of files) {
  try {
    console.log('ok  ' + (await shoot(browser, file)).replace(root + '/', ''));
  } catch (error) {
    failed += 1;
    console.log('ERR ' + file + ': ' + error.message);
  }
}
await browser.close();
console.log(`${files.length - failed} screenshots, ${failed} failed`);
process.exit(failed ? 1 : 0);
