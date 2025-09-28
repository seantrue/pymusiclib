#!/bin/bash
. .venv/bin/activate
itlib-export new.csv --date-added-after 2025-09-15
python conductor.py
get_cover_art --art-dest-inline --path plex
rsync -av plex/* /Volumes/data_media/Music/
