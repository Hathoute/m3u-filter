#!/usr/bin/env bash
set -e

function cleanup {
  rm -f full.m3u
}
trap cleanup EXIT

if [ -e .env ]
then
  export $(cat .env | xargs)
fi

LAST_MD5=""
if [ -e ./tv.md5 ]; then
    LAST_MD5=$(<./tv.md5)
fi

wget -O full.m3u $M3U_URL
FULL_MD5=($(md5sum full.m3u))

if [ "$FULL_MD5" = "$LAST_MD5" ]; then
  echo "M3U file did not change from last filter, skipping..."
  exit 0
else
  echo "M3U file changed, filtering..."
fi

echo $FULL_MD5 > ./tv.md5

pip3 install -r requirements.txt
python3 main.py full.m3u filtered.m3u

exit 0