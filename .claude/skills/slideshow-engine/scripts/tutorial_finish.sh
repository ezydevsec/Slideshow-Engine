#!/usr/bin/env bash
# Tutorial finisher: download a Kling clip, stabilise it (vidstab tripod, Kling drifts the camera), loop it.
#   tutorial_finish.sh <url> <slug> <pingpong|full> [out_root]
# pingpong = clip is start→end half-rep (forward + reverse); full = clip is one whole rep.
set -euo pipefail
URL=$1; SLUG=$2; MODE=$3; ROOT=${4:-05-tutorials/v2}
D=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$ROOT/raw" "$ROOT/out"; TRF=$(mktemp --suffix=.trf)
curl -s -o "$ROOT/raw/$SLUG.mp4" "$URL"
ffmpeg -v error -y -i "$ROOT/raw/$SLUG.mp4" -vf vidstabdetect=tripod=1:result="$TRF" -f null -
ffmpeg -v error -y -i "$ROOT/raw/$SLUG.mp4" -vf vidstabtransform=tripod=1:input="$TRF":zoom=4:optzoom=0,unsharp=5:5:0.6 -c:v libx264 -crf 16 "$ROOT/raw/$SLUG-stab.mp4"
rm -f "$TRF"
if [ "$MODE" = pingpong ]; then python3 "$D/tutorial_loop.py" "$ROOT/raw/$SLUG-stab.mp4" "$ROOT/out" "$SLUG" --pingpong
else python3 "$D/tutorial_loop.py" "$ROOT/raw/$SLUG-stab.mp4" "$ROOT/out" "$SLUG"; fi
