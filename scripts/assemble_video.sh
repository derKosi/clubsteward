#!/usr/bin/env bash
# Assemble docs/video/clubsteward-demo-v2.mp4 from the beat clips + v4 voiceover.
# Cut points derived from event mtimes (see conversation log 13.09.):
#   04-step: Danny decision @18s, picture-day draft @96s (retake-3)
#   05-morning: approve toast @80s  |  08-runnight: stop toast @~55s
set -euo pipefail

BIN=/c/Users/Nutzer/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.1-full_build/bin
FF=$BIN/ffmpeg.exe
FP=$BIN/ffprobe.exe
SRC=/c/Dev/derKosi/clubsteward/docs/video/clips-v2
VO=/c/Dev/derKosi/clubsteward/docs/voiceover-v4
WORK=/c/Dev/derKosi/video-assemble
WINSRC=C:/Dev/derKosi/clubsteward/docs/video/clips-v2
WINWORK=C:/Dev/derKosi/video-assemble
OUT=/c/Dev/derKosi/clubsteward/docs/video/clubsteward-demo-v2.mp4

rm -rf "$WORK"; mkdir -p "$WORK"
V="-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30"

# cut <webm-stem> <sub-tag> <from> <to> [extra-vf]
cutseg() {
  local stem=$1 tag=$2 from=$3 to=$4 vf=${5:-}
  if [ -n "$vf" ]; then vf="-vf $vf"; fi
  "$FF" -y -v error -i "$SRC/$stem.webm" -ss "$from" -to "$to" $V $vf -an "$WORK/$stem-$tag.mp4"
}

# joinvids <out> <sub-file...>  — concat sub-segments of one beat (stream copy)
joinvids() {
  local out=$1; shift
  : > "$WORK/lst.txt"
  for t in "$@"; do echo "file '$WINWORK/$t.mp4'" >> "$WORK/lst.txt"; done
  "$FF" -y -v error -f concat -safe 0 -i "$WORK/lst.txt" -c copy "$WORK/$out.mp4"
}

# muxav <beat> <audio-filter> <audio-inputs...>  — VO under the joined beat video
muxav() {
  local beat=$1 afilter=$2; shift 2
  local inputs=() i=0
  for f in "$@"; do inputs+=(-i "$VO/$f"); i=$((i+1)); done
  "$FF" -y -v error -i "$WORK/$beat.mp4" "${inputs[@]}" \
    -filter_complex "$afilter" -map 0:v -map "[a]" \
    -c:v copy -c:a aac -b:a 128k -ac 2 -ar 44100 -shortest "$WORK/final-$beat.mp4"
}

MONO="[1:a]adelay=400:all=1,apad[a]"

# ---- 01 hook (28s, fade in) ----
cutseg 01-hook a 0 28 "fade=t=in:st=0:d=0.5"
joinvids 01-hook 01-hook-a
muxav 01-hook "$MONO" 01-hook.mp3

# ---- 02 intro (22s) ----
cutseg 02-intro a 0 22
joinvids 02-intro 02-intro-a
muxav 02-intro "$MONO" 02-intro.mp3

# ---- 03 reset (16s) ----
cutseg 03-reset a 0 16
joinvids 03-reset 03-reset-a
muxav 03-reset "$MONO" 03-reset.mp3

# ---- 04 step: A mail+click1 | B result1+click2 | C mail2 | D result2 ----
cutseg 04-step a 0 8.5
cutseg 04-step b 16.5 27
cutseg 04-step c 27 34
cutseg 04-step d 94.5 105
joinvids 04-step 04-step-a 04-step-b 04-step-c 04-step-d
muxav 04-step "$MONO" 04-step.mp3

# ---- 05 morning: cards+typing+approve | toast+aftermath ----
cutseg 05-morning a 0 21
cutseg 05-morning b 78 90
joinvids 05-morning 05-morning-a 05-morning-b
muxav 05-morning "$MONO" 05-morning.mp3

# ---- 06 outbox (23s) ----
cutseg 06-outbox a 0 23
joinvids 06-outbox 06-outbox-a
muxav 06-outbox "$MONO" 06-outbox.mp3

# ---- 07 anylanguage (31s): EN1 @0.5s / DE @10s / EN2 @21.5s ----
cutseg 07-anylanguage a 0 31
joinvids 07-anylanguage 07-anylanguage-a
muxav 07-anylanguage \
  "[1:a]adelay=500:all=1[a1];[2:a]adelay=10000:all=1[a2];[3:a]adelay=21500:all=1[a3];[a1][a2][a3]amix=inputs=3:normalize=0,apad[a]" \
  07-anylanguage-en1.mp3 07-anylanguage-de.mp3 07-anylanguage-en2.mp3

# ---- 08 runnight: click+log | streaming+stop | toast ----
cutseg 08-runnight a 0 4.5
cutseg 08-runnight b 18 26
cutseg 08-runnight c 53 60
joinvids 08-runnight 08-runnight-a 08-runnight-b 08-runnight-c
muxav 08-runnight "$MONO" 08-runnight.mp3

# ---- 09 built (29s) ----
cutseg 09-built a 0 29
joinvids 09-built 09-built-a
muxav 09-built "$MONO" 09-built.mp3

# ---- 10 close (14s, fade out) ----
cutseg 10-close a 0 14 "fade=t=out:st=12.9:d=1"
joinvids 10-close 10-close-a
muxav 10-close "$MONO" 10-close.mp3

# ---- final concat (re-encode once for uniform stream) ----
: > "$WORK/final.txt"
for b in 01-hook 02-intro 03-reset 04-step 05-morning 06-outbox 07-anylanguage 08-runnight 09-built 10-close; do
  echo "file '$WINWORK/final-$b.mp4'" >> "$WORK/final.txt"
done
"$FF" -y -v error -f concat -safe 0 -i "$WORK/final.txt" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 128k -ac 2 -ar 44100 -movflags +faststart "$OUT"

echo "=== fertig ==="
"$FP" -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
