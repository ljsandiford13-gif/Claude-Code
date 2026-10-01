// Renders showreel.html frame by frame with headless Chromium.
//
//   node render.mjs                         every frame, with motion blur, into ./build/sub
//   node render.mjs --stills 0.5,2.1,7.4    single clean frames into ./build/stills
//   node render.mjs --from 60 --to 90       a frame range
//   node render.mjs --cues                  writes build/cues.json for the soundtrack
//   node render.mjs --cover                 writes build/cover_raw.png, the grid cover
//   add --bg 1 to render the water background at full size (slower, near identical)
//
// Motion blur: fast frames are sampled several times across a 180 degree shutter.
// The page reports how far its fastest element moves per frame (window.speed) and
// we take one sample per ~3px of smear. compose.py averages the samples.
import { execSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf('--' + name); return i < 0 ? def : args[i + 1]; };
const flag = name => args.includes('--' + name);

async function loadPlaywright() {
  try { return await import('playwright'); } catch {}
  const root = execSync('npm root -g').toString().trim();
  return import(pathToFileURL(join(root, 'playwright', 'index.mjs')).href);
}

const SHUTTER = 0.5;   // 180 degrees
const MAX_SUB = 24;

const { chromium } = await loadPlaywright();
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-lcd-text', '--font-render-hinting=none'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('page error:', e.message); process.exit(1); });
await page.goto(pathToFileURL(join(here, 'showreel.html')).href + (opt('bg') ? '?bg=' + opt('bg') : ''));
await page.evaluate(() => window.ready);
const META = await page.evaluate(() => window.META);
const cdp = await page.context().newCDPSession(page);

async function shoot(t, file) {
  await page.evaluate(t => window.seek(t), t);
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false, optimizeForSpeed: true });
  writeFileSync(file, Buffer.from(data, 'base64'));
}

if (flag('cues')) {
  const cues = await page.evaluate(() => window.CUES);
  mkdirSync(join(here, 'build'), { recursive: true });
  writeFileSync(join(here, 'build', 'cues.json'), JSON.stringify({ meta: META, cues }, null, 2));
  console.log('wrote build/cues.json');
} else if (flag('cover')) {
  // The hook, restyled, without the cursor or selection box: the reel's grid cover.
  mkdirSync(join(here, 'build'), { recursive: true });
  await page.evaluate(t => window.seek(t), 2.3);
  await page.evaluate(async () => {
    for (const el of document.querySelectorAll('.cursor, #s1-sel')) el.style.opacity = 0;
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(join(here, 'build', 'cover_raw.png'), Buffer.from(data, 'base64'));
  console.log('wrote build/cover_raw.png');
} else if (opt('stills')) {
  const out = opt('out', join(here, 'build', 'stills'));
  mkdirSync(out, { recursive: true });
  for (const s of opt('stills').split(',')) {
    const t = parseFloat(s);
    const file = join(out, `t${t.toFixed(2).padStart(5, '0')}.png`);
    await shoot(t, file);
    console.log(file);
  }
} else {
  const out = opt('out', join(here, 'build', 'sub'));
  mkdirSync(out, { recursive: true });
  const total = Math.round(META.DUR * META.FPS);
  const from = parseInt(opt('from', '0')), to = parseInt(opt('to', String(total)));
  const fixed = opt('sub') ? parseInt(opt('sub')) : 0;
  const plan = {};
  const t0 = Date.now();
  for (let f = from; f < to; f++) {
    const t = f / META.FPS;
    const spd = await page.evaluate(t => window.speed(t), t);
    const n = fixed || Math.max(1, Math.min(MAX_SUB, Math.ceil(spd * SHUTTER / 3)));
    plan[f] = n;
    for (let k = 0; k < n; k++) {
      const ts = n === 1 ? t : t + ((k + 0.5) / n - 0.5) * SHUTTER / META.FPS;
      const tc = Math.min(Math.max(ts, 0), META.DUR - 1e-4);
      await shoot(tc, join(out, `f${String(f).padStart(4, '0')}_${String(k).padStart(2, '0')}.png`));
    }
    if (f % 15 === 0) console.log(`frame ${f}  samples ${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  writeFileSync(join(out, `plan_${from}_${to}.json`), JSON.stringify(plan));
}
await browser.close();
