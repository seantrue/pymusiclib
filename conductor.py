import os
import shutil
import pandas as pd
df = pd.read_csv("new.csv").fillna("")

for isong, song in df.iterrows():
    if not song.file_path or not song.track_number:
        print(f"Skipping {song.album} {song.title}")
        continue
    ext = song.file_extension
    if not song.file_path.endswith(ext):
        print(f"Ending {ext} mismatch for {song.file_path}")
        continue
    artist = song.album_artist if song.album_artist else song.artist
    path = f"plex/{artist}/{song.album}/{int(song.track_number):02d} - {song.title}.{ext}"
    if os.path.exists(path):
        print(f"{song.artist} - {song.album} {song.title} exists")
        continue
    dirname = os.path.dirname(path)
    os.makedirs(dirname,exist_ok=True)
    print(f"Copying {song.artist} - {song.name}")
    shutil.copy(song.file_path, path)
                              
                           
                           
    

