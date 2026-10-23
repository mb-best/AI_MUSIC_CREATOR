#!/bin/sh
# Linux / macOS: sh build.sh [your_song.py] [--output-dir DIR]
set -e
echo '免费分享 · 禁止售卖 · 禁止以任何名义收费（CC BY-NC-SA 4.0，创作者 reaesteve）'
echo 'Shared free · Not for sale · No paid access of any kind (CC BY-NC-SA 4.0, creator: reaesteve)'
cd "$(dirname "$0")"
exec python3 build.py "$@"
