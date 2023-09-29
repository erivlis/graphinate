import json
from collections import defaultdict

with open("albums.json") as f:
    albums = json.load(f)

artist_titles = defaultdict(list)
title_performers = defaultdict(set)
performer_instruments = defaultdict(set)
for album in albums:
    artist_titles[album.get('Artist')].append(album.get('Title'))
    performers = [tuple(p.strip().split(':')) for p in album.get('Performer').split('/')]
    for items in performers:
        performer = items[0].strip()
        title_performers[album.get('Title')].add(performer)

        if len(items) > 1:
            for instrument in items[1].strip().split(','):
                performer_instruments[performer].add(instrument)

print('a')
