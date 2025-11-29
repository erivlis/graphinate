import json
import pathlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from lxml import etree


def file_path(file: str) -> pathlib.Path:
    current_script_path = pathlib.Path(__file__).resolve()
    parent_dir = current_script_path.parent
    return parent_dir / file


def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}


@dataclass
class Entry:
    artist: str
    title: str
    type: str
    time: timedelta
    genre: str
    label: str
    performers: set[str]
    year: int
    added: datetime


def albums_():
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


if __name__ == "__main__":
    tree = etree.parse(file_path('db.xml'))
    root = tree.getroot()
    data_dict = xml_to_dict(root)
    print(data_dict)
