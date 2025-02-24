import logging
import operator
from time import sleep

import diskcache
import musicbrainzngs

import graphinate

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_musicbrainz():
    musicbrainzngs.set_useragent(
        "MusicGraph",
        "0.1.0",
        "https://github.com/erivlis"
    )


initialize_musicbrainz()


def music_graph_model(name: str, max_depth: int = 0):
    graph_model = graphinate.model(f"{name.capitalize()} Graph")

    artists_cache = diskcache.Cache(directory=r'C:\dev\erivlis\graphinate\examples\system', eviction_policy='none')

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
    model = None
    for name in [
        'Beatles',
        'Caravan',
        'Emerson, Lake & Palmer',
        'Gentle Giant',
        'Genesis',
        'King Crimson',
        'Jethro Tull',
        'Pink Floyd',
        'Police',
        'Porcupine Tree',
        'Rush',
        'Soft Machine',
        'Yes',
        'System of a Down',
        'Pearl Jam',
        'Soundgarden',
        'Nirvana',
        'Alice in Chains',
        'Stone Temple Pilots',
        'Foo Fighters',
        'Red Hot Chili Peppers',
        'Smashing Pumpkins',
        'Radiohead',
        'David Bowie',
        'Led Zeppelin',
        'Deep Purple',
        'Wings',
        'Paul McCartney',
        'Mahavishnu Orchestra',
        'Miles Davis',
        'John Coltrane',
        'Frank Zappa',
        'Charles Mingus',
        'Thelonious Monk',
        'Ornette Coleman',
        'Weather Report',
        'Return to Forever',
        'Herbie Hancock',
        'Dire Straits',
        'John Zorn',
        'Dave Brubeck',
        'Dave Douglas',
        'Ken Vandermark',
        'John Scofield',
    ]:
        artist_model = music_graph_model(name, 2)
        model = artist_model if model is None else model + artist_model

    graphinate.materialize(
        model,
        builder=graphinate.builders.GraphQLBuilder,
        builder_output_handler=graphinate.graphql
    )
