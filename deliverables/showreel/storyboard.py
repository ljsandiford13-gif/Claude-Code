#!/usr/bin/env python3
"""Makes storyboard.png: key frames from the finished frames, five per row, with timecodes."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FPS = 30
TIMES = [0.9, 2.3, 3.75, 4.6, 5.2, 5.85, 6.7, 7.7, 8.7, 10.6, 11.4, 11.8, 12.6, 13.4, 14.9]
SCALE = 0.25
GAP = 16
LABEL = 34
font = ImageFont.load_default(size=20)

frames = [Image.open(HERE / 'build' / 'frames' / f'f{round(t * FPS):04d}.png').convert('RGB') for t in TIMES]
w, h = int(1080 * SCALE), int(1920 * SCALE)
cols = 5
rows = (len(frames) + cols - 1) // cols
sheet = Image.new('RGB', (GAP + cols * (w + GAP), GAP + rows * (h + LABEL + GAP)), (4, 32, 46))
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(zip(TIMES, frames)):
    x = GAP + (i % cols) * (w + GAP)
    y = GAP + (i // cols) * (h + LABEL + GAP)
    d.text((x, y + 8), f'{t:05.2f}s', fill=(234, 247, 250), font=font)
    sheet.paste(im.resize((w, h), Image.LANCZOS), (x, y + LABEL))
sheet.save(HERE / 'storyboard.png', optimize=True)
print('storyboard.png', sheet.size)
