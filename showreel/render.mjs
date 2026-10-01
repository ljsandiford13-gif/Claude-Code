// Renders showreel/index.html frame by frame through headless Chromium, then encodes with ffmpeg.
// Usage:
//   node render.mjs                         full 15 s render to out/showreel-1920x1080.mp4
//   node render.mjs --stills=0.5,2.6,7.9    QA stills only (out/stills/t_*.png)
//   node render.mjs --audio=out/bed.wav     mux a sound bed
//   node render.mjs --w=1080 --h=1920       other canvas sizes (the page must support them)
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).map(a => { const m = a.replace(/^--/, '').split('='); return [m[0], m.length > 1 ? m.slice(1).join('=') : true]; }));
const W = +args.w || 1920, H = +args.h || 1080, FPS = +args.fps || 30, DUR = +args.dur || 15;
const N = Math.round(FPS * DUR);
const outDir = path.resolve(here, args.outdir || 'out');
const framesDir = path.join(outDir, args.framesdir || 'frames');
const stillsDir = path.join(outDir, 'stills');
const outFile = path.resolve(here, args.out || `out/showreel-${W}x${H}.mp4`);
const pageUrl = 'file://' + path.join(here, 'index.html') + `?render=1&w=${W}&h=${H}`;

fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text', '--hide-scrollbars'] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
await page.goto(pageUrl);
await page.evaluate(() => window.__ready);
const settle = () => page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));

if (args.stills) {
  fs.mkdirSync(stillsDir, { recursive: true });
  for (const t of String(args.stills).split(',').map(Number)) {
    await page.evaluate(([t, f]) => window.__seek(t, f), [t, Math.round(t * FPS)]);
    await settle();
    const f = path.join(stillsDir, `t_${t.toFixed(2).replace('.', '_')}.png`);
    await page.screenshot({ path: f, type: 'png' });
    console.log('still', f);
  }
  await browser.close();
  process.exit(process.exitCode || 0);
}

fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });
const t0 = Date.now();
for (let f = 0; f < N; f++) {
  await page.evaluate(([t, f]) => window.__seek(t, f), [f / FPS, f]);
  await settle();
  await page.screenshot({ path: path.join(framesDir, `f${String(f).padStart(4, '0')}.png`), type: 'png' });
  if (f % 30 === 0) console.log(`frame ${f}/${N}  ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}
await browser.close();
console.log(`captured ${N} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);

const ff = ['-y', '-framerate', String(FPS), '-i', path.join(framesDir, 'f%04d.png')];
if (args.audio) ff.push('-i', path.resolve(here, args.audio));
ff.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
  '-vf', 'format=yuv420p', '-r', String(FPS));
if (args.audio) ff.push('-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest');
ff.push('-movflags', '+faststart', '-t', String(DUR), outFile);
console.log('ffmpeg', ff.join(' '));
const r = spawnSync('ffmpeg', ff, { stdio: ['ignore', 'inherit', 'pipe'] });
if (r.status !== 0) { console.error(String(r.stderr).split('\n').slice(-25).join('\n')); process.exit(1); }
console.log('wrote', outFile, (fs.statSync(outFile).size / 1e6).toFixed(1), 'MB');
if (!args.keepframes) fs.rmSync(framesDir, { recursive: true, force: true });
