import logging
import operator
import pathlib
from functools import reduce
from time import sleep

import diskcache
import musicbrainzngs

import graphinate

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_musicbrainz():
    musicbrainzngs.set_useragent(
        "MusicArtistGraph",
        "0.1.0",
        "https://github.com/erivlis/graphinate"
    )


initialize_musicbrainz()


def cache_dir():
    current_script_path = pathlib.Path(__file__).resolve()
    parent_dir = current_script_path.parent
    return (parent_dir / 'cache').as_posix()


def music_graph_model(name: str, max_depth: int = 0):
    graph_model = graphinate.model(f"{name.capitalize()} Graph")

    artists_cache = diskcache.Cache(directory=cache_dir(), eviction_policy='none')

    result = musicbrainzngs.search_artists(query=name, strict=True, artist=name)
    sleep(1)
    root_artist = result.get('artist-list', [])[0] if result else None

    def artists(parent_artist, artist, depth):
        logger.info(f"Current depth: {depth}")
        artist_id = artist.get('id')
        if artist_id not in artists_cache:
            artists_cache[artist_id] = musicbrainzngs.get_artist_by_id(id=artist_id, includes=['artist-rels']).get(
                'artist')
            sleep(0.1)

        artist = artists_cache.get(artist_id)

        yield parent_artist, artist

        if depth < max_depth:
            related_artist_ids = set()
            for item in artist.get('artist-relation-list', []):
                related_artist = item.get('artist')
                related_artist_id = related_artist.get('id')
                if related_artist_id not in related_artist_ids:
                    related_artist_ids.add(related_artist_id)
                    yield from artists(artist, related_artist, depth + 1)

    def artist_type(value):
        return value.get('type', '_UNKNOWN_')

    @graph_model.node(artist_type,
                      key=operator.itemgetter('id'),
                      label=operator.itemgetter('name'),
                      multiplicity=graphinate.Multiplicity.FIRST)
    def node():
        yielded = set()
        for a, b in artists(None, root_artist, 0):
            if a and ((a_id := a.get('id')) not in yielded):
                yielded.add(a_id)
                yield a
            if b and ((b_id := b.get('id')) not in yielded):
                yielded.add(b_id)
                yield b

    @graph_model.edge()
    def edge():
        for a, b in artists(None, root_artist, 0):
            if a:
                yield {'source': a.get('id'), 'target': b.get('id')}

    return graph_model


if __name__ == '__main__':
    from gui import ListboxChooser

    artist_names = [
        'Alice in Chains',
        'Beatles',
        'Caravan',
        'Charles Mingus',
        'Dave Brubeck',
        'Dave Douglas',
        'David Bowie',
        'Deep Purple',
        'Dire Straits',
        'Emerson, Lake & Palmer',
        'Foo Fighters',
        'Frank Zappa',
        'Genesis',
        'Gentle Giant',
        'Herbie Hancock',
        'Jethro Tull',
        'John Coltrane',
        'John Scofield',
        'John Zorn',
        'Ken Vandermark',
        'King Crimson',
        'Led Zeppelin',
        'Mahavishnu Orchestra',
        'Miles Davis',
        'Nirvana',
        'Ornette Coleman',
        'Paul McCartney',
        'Pearl Jam',
        'Pink Floyd',
        'Police',
        'Porcupine Tree',
        'Radiohead',
        'Red Hot Chili Peppers',
        'Return to Forever',
        'Rush',
        'Smashing Pumpkins',
        'Soft Machine',
        'Soundgarden',
        'Stone Temple Pilots',
        'System of a Down',
        'Thelonious Monk',
        'Weather Report',
        'Wings',
        'Yes',
    ]

    listbox_chooser = ListboxChooser('Choose Artist/s', {name: name for name in artist_names})

    models = (music_graph_model(a, 2) for _, a in listbox_chooser.get_choices())

    model = reduce(operator.add, models)

    schema = graphinate.builders.GraphQLBuilder(model).build()
    graphinate.graphql.server(schema)
