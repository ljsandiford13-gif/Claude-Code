#!/usr/bin/env bash
# Procedural sound bed for the showreel: filtered sea noise with a slow swell, a low thump on the dive,
# soft ticks on each scene change and a quiet pad under the sign off. Swap for a licensed track any time:
#   node render.mjs --audio=path/to/track.wav
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
ffmpeg -y -loglevel error \
  -f lavfi -i "anoisesrc=color=brown:seed=7:amplitude=0.7:duration=15:sample_rate=48000" \
  -f lavfi -i "aevalsrc='0.42*sin(2*PI*52*t)*exp(-3.2*max(t-2.35,0))*gte(t,2.35) + 0.3*sin(2*PI*46*t)*exp(-3.4*max(t-13.05,0))*gte(t,13.05) + 0.14*(sin(2*PI*55*t)+0.5*sin(2*PI*82.5*t))*min(max(t-13.4,0),1)':s=48000:d=15" \
  -f lavfi -i "aevalsrc='(random(0)-0.5)*(exp(-90*max(t-5.5,0))*gte(t,5.5) + exp(-90*max(t-7.55,0))*gte(t,7.55) + exp(-90*max(t-8.5,0))*gte(t,8.5) + exp(-90*max(t-9.3,0))*gte(t,9.3) + exp(-90*max(t-11.6,0))*gte(t,11.6))':s=48000:d=15" \
  -filter_complex "[0]lowpass=f=340,tremolo=f=0.11:d=0.6,volume=1.0[sea];[1]lowpass=f=220[low];[2]highpass=f=1600,lowpass=f=7000,volume=0.5[tick];[sea][low][tick]amix=inputs=3:normalize=0,afade=t=in:d=0.9,afade=t=out:st=13.6:d=1.4,loudnorm=I=-20:TP=-2:LRA=9[a]" \
  -map "[a]" -ar 48000 -ac 2 out/bed.wav
ffmpeg -loglevel info -i out/bed.wav -af "ebur128=peak=true" -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
echo "wrote out/bed.wav"
