# Sandiford Digital showreel

A 15 second motion graphics piece, 1920 x 1080 at 30 fps, built on the Sandiford Digital brand system
(tidal depth: foam surface down to deep water, Fraunces headlines, JetBrains Mono labels, one aqua line,
coral as a flare). Everything is rendered from `index.html`, so every frame is a pure function of time.

## Files

| Path | What it is |
|---|---|
| `index.html` | The composition. Open it in a browser to watch it loop. Add `?t=7.4` to freeze a frame. |
| `render.mjs` | Headless Chromium frame capture plus ffmpeg encode. |
| `audio.sh` | Procedural sound bed (filtered sea noise, a thump on the dive, soft ticks on cuts). |
| `fonts/` | Fraunces, Manrope and JetBrains Mono as woff2, served locally so renders are deterministic. |
| `assets/` | Drop `logo.png` (the colour S mark on transparent) here and it appears above the sign off. |
| `out/` | Render output. The finished MP4 is copied to `../deliverables/`. |

## Render

```bash
cd showreel
./audio.sh                                   # writes out/bed.wav
node render.mjs --audio=out/bed.wav          # writes out/showreel-1920x1080.mp4 (about 2 minutes)
node render.mjs --stills=0.9,7.4,14.6        # QA stills in out/stills/
node render.mjs --audio=path/to/track.wav    # swap in a licensed track
```

The renderer imports Playwright from the global install at `/opt/node-tools/node_modules`. On another
machine, `npm i playwright` and change the import at the top of `render.mjs`.

## Timeline

| Time | Field | What happens |
|---|---|---|
| 0.0 to 2.4 | foam | Chrome draws in. "Your customers are Googling you. *Nothing comes up.*" rises word by word over drifting tide lines. |
| 2.4 to 3.0 | | Deep water rises from the bottom edge with an aqua waterline. |
| 3.0 to 5.5 | deep | 01 We build the site. 02 We write the words. 03 We send the numbers *every month.* |
| 5.5 to 9.3 | deep | A browser frame draws itself in hairline, a bakery site assembles element by element, a phone joins it, then a salon site and a car rental site rise through both frames. |
| 9.3 to 11.6 | shallow | "Every month, the numbers *in plain English.*" beside a report card whose two lines draw in. |
| 11.6 to 13.0 | coral | A coral field wipes in from the left: "Message us *on WhatsApp.*" |
| 13.0 to 15.0 | deep | Deep water rises again for the typographic sign off: Sandiford / *Digital.* |

## Brand notes

- Only the seven brand colours and three brand fonts are used. Ink on aqua and coral is always deep.
- One italic accent phrase per scene. One coral element per scene (the coral field counts as the one).
- Chrome on every scene: aqua rule plus mono eyebrow top left, counter top right, `@sandiford.digital`
  bottom left, site address bottom right. Chrome ink flips per field as each wipe passes it.
- Motion follows the brand spec: words rise 115 percent from behind a mask (ease out quint, 0.09 s
  stagger), groups rise 40 px (ease out expo), wipes and rules use ease in out quint. Nothing bounces.
- Film grain overlay, soft light, about 5 percent.
- The mock sites use generic trade names (Bakery, Salon, Rentals) so nothing reads as an invented client.
- The report chart has no numerals, so it shows the shape of a report without inventing results.
- The logo mark is not redrawn. The typographic sign off stands in until `assets/logo.png` is supplied.
