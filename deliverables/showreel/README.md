# Sandiford Digital showreel, 15 seconds

A reel built entirely in the brand system: tidal depth, from foam down to the deep.

| File | What it is |
|---|---|
| `Sandiford_Digital_Showreel_15s.mp4` | The reel. 1080 x 1920, 30fps, H.264 with AAC sound at -14 LUFS. |
| `Sandiford_Digital_Showreel_15s_silent.mp4` | Same picture, no sound, for adding a track in the Instagram editor. |
| `cover.png` | Grid cover: the hook slide, restyled. |
| `storyboard.png` | Key frames from all five slides. |

## The five slides

| Time | Slide | Field | Copy |
|---|---|---|---|
| 0.0 to 2.5 | 01 Web design, Bridgetown | Foam | Your customers are *Googling you.* The phrase is selected and restyled live, italic teal. |
| 2.5 to 6.0 | 02 Design and build | Deep | Designed and built *on the island.* The page sinks below the waterline, a browser draws on, a 12 column grid and wireframe build, a block is dragged onto the grid, the finished site fills in, then it reflows into a phone. |
| 6.0 to 9.0 | 03 Who we build for | Deep | Garages. Barbers. *Roti shops.* One site per word, with a big mono index numeral. |
| 9.0 to 11.5 | 04 Monthly reports | Aqua | A report every month. *In plain English.* A tide line draws through the months, ending on one coral dot. |
| 11.5 to 15.0 | 05 Get in touch | Deep | Sandiford *Digital.* Message us on WhatsApp. |

Cuts sit on a 120 BPM grid, so the drop into deep water, each site swap and the sign off land on the beat.

## Brand checks

- Colours: deep, shallow, foam, aqua, teal (on foam only), coral. Nothing else, no gradients except the radial vignette behind the sign off.
- Type: Fraunces 340 headlines with one italic accent phrase per slide, Manrope for UI, JetBrains Mono uppercase for labels and numerals.
- At most one coral element per slide: the roti order button, the chart dot, the WhatsApp button.
- Chrome on every slide: aqua rule, eyebrow, counter, `@sandiford.digital`, site address. Text stays inside the story safe zone (250px top, 340px bottom).
- Motion: masked rises at 115 percent with ease out quint, group reveals with ease out expo, wipes and rules with ease in out quint. No bounces or spins. Film grain at 5 percent, soft light.
- No dashes as punctuation, no hype words, no invented clients, results or numbers. The sites are studio made examples for the kinds of businesses the studio builds for, with no business names on them.

## Still to do: the logo

The full colour mark could not be fetched in the session that built this (the Bloom file store was not reachable), and the brand rules say never to redraw it. Save it as `assets/logo.png` (transparent background) and re-render. The sign off makes room above the wordmark and the mark rises in with it.

## Re-rendering

Needs Node with Playwright and Chromium, Python 3 with numpy, scipy, Pillow (pyloudnorm optional), and ffmpeg.

```sh
node render.mjs --cues     # sound cue list from the timeline
python3 audio.py           # soundtrack
node render.mjs            # every frame with motion blur, about 15 minutes on 4 cores
                           # (split across processes with --from N --to M)
node render.mjs --cover
python3 compose.py         # blur, grain, encode both MP4s, cover
```

`showreel.html` is the whole piece. Open it in a browser with `?play` to watch it live or `?t=7.5` to hold a frame. Copy lives in the markup, and every cut point lives in the `T` table near the top of the script. Change a time there and the sound cues follow it.

The soundtrack is synthesised in `audio.py`, so there is nothing to license. Word reveals play soft droplet notes from the current chord, panned to where each word sits on screen.

Fonts are from Google Fonts under the SIL Open Font License.
