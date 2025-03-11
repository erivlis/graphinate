# Tutorial

This tutorial will guide you through the steps to create a **Music Artists Graph**.
(It is based on the [Music Artists](/examples/social/#music-artists) example).

## Prerequisites

Before you begin, please ensure you have installed the following dependencies:

- Python 3.10 or above
- `pip` (Python package installer)
- Required Python packages: `diskcache`, `musicbrainzngs`, `graphinate`

You can install the required packages using the following command:

```shell
pip install diskcache musicbrainzngs graphinate
```

## Step 1: Initialize MusicBrainz

First, we need to initialize the MusicBrainz client with a user agent. This helps identify the application when making
requests to the MusicBrainz API.

```python
import musicbrainzngs


def initialize_musicbrainz():
    musicbrainzngs.set_useragent(
        "MusicArtistGraph",
        "0.1.0",
        "https://github.com/erivlis/graphinate"
    )


initialize_musicbrainz()
```

## Step 2: Set Up Caching

We will use `diskcache` to cache artist data to avoid redundant API calls.
(A prefilled cache may be available in the GitHub repo).

```python
import pathlib
import diskcache


def cache_dir():
    current_script_path = pathlib.Path(__file__).resolve()
    parent_dir = current_script_path.parent
    return (parent_dir / 'cache').as_posix()


artists_cache = diskcache.Cache(directory=cache_dir(), eviction_policy='none')
```

## Step 3: Create the Graph Model

### Step 3.1: Import Required Modules

We need to import the necessary modules for creating the graph model.

```python
import graphinate
from time import sleep
import operator
```

### Step 3.2: Define the Music Graph Model Function

We will create a function `music_graph_model` that takes an artist's name and a maximum depth of recursion.
This function will be used to create a Graph Model.

```python
def music_graph_model(name: str, max_depth: int = 0) -> graphinate.GraphModel:
    graph_model = graphinate.model(f"{name.capitalize()} Graph")
```

### Step 3.3: Search for the Root Artist

We will search for the root artist using the MusicBrainz API.

```python
    result = musicbrainzngs.search_artists(query=name, strict=True, artist=name)
sleep(1)  # Sleep for 1 second to avoid rate limiting
root_artist = result.get('artist-list', [])[0] if result else None
```

### Step 3.4: Define the Artists Generator Function

We will define a generator function `artists` to yield parent and related artists recursively.
We will retrieve the artist data from the cache if it exists, otherwise, we will fetch it from the MusicBrainz API.
Then we will yield the parent and related artists. If the depth is less than the maximum depth, we will recursively
yield artists for each related artist as a starting point.

```python
    def artists(parent_artist, artist, depth):
    artist_id = artist.get('id')
    if artist_id not in artists_cache:
        artists_cache[artist_id] = musicbrainzngs.get_artist_by_id(id=artist_id, includes=['artist-rels']).get('artist')
        sleep(0.1)  # Sleep for 0.1 second to avoid rate limiting

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
```

### Step 3.5: Define the Artist Type Function

We will define a function to get the type of an artist. We'll use it in the next step

```python
    def artist_type(value):
    return value.get('type', '_UNKNOWN_')
```

### Step 3.6: Define the Node Model

We will define the node model for the graph using the `node` decorator.
Using the musicbrainz artist type as the node type, the artist ID as the node key, and the artist name as the label.
The `Multiplicity.FIRST` option ensures that only the first occurrence of an artist is included in the graph.

```python
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
```

### Step 3.7: Define the Edge Model

We will define the edge model for the graph to represent relationships between artists.

```python
    @graph_model.edge()
def edge():
    for a, b in artists(None, root_artist, 0):
        if a:
            yield {'source': a.get('id'), 'target': b.get('id')}
```

### Step 3.8: Return the Graph Model

Putting it all together and, Finally, return the created graph model.

```python
import graphinate
import musicbrainzngs
from time import sleep
import operator
import diskcache
import pathlib


def cache_dir():
    current_script_path = pathlib.Path(__file__).resolve()
    parent_dir = current_script_path.parent
    return (parent_dir / 'cache').as_posix()


artists_cache = diskcache.Cache(directory=cache_dir(), eviction_policy='none')


def music_graph_model(name: str, max_depth: int = 0):
    graph_model = graphinate.model(f"{name.capitalize()} Graph")

    result = musicbrainzngs.search_artists(query=name, strict=True, artist=name)
    sleep(1)  # Sleep for 1 second to avoid rate limiting
    root_artist = result.get('artist-list', [])[0] if result else None

    def artists(parent_artist, artist, depth):
        artist_id = artist.get('id')
        if artist_id not in artists_cache:
            artists_cache[artist_id] = musicbrainzngs.get_artist_by_id(id=artist_id, includes=['artist-rels']).get(
                'artist')
            sleep(0.1)  # Sleep for 0.1 second to avoid rate limiting

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

    @graph_model.node(artist_type, key=operator.itemgetter('id'), label=operator.itemgetter('name'),
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
```

## Step 4: Create the GUI for Artist Selection

### Step 4.1: Import Required Modules

We will use `tkinter` to create a simple GUI for selecting artists.
Implemented before hand in the `gui.py` file located in the example folder.

```python
from gui import ListboxChooser
```

### Step 4.2: Define the Artist Names

We will define a list of artist names to be displayed in the listbox.

```python
artist_names = [
    'Alice in Chains', 'Beatles', 'Caravan', 'Charles Mingus', 'Dave Brubeck',
    'Dave Douglas', 'David Bowie', 'Deep Purple', 'Dire Straits', 'Emerson, Lake & Palmer',
    'Foo Fighters', 'Frank Zappa', 'Genesis', 'Gentle Giant', 'Herbie Hancock',
    'Jethro Tull', 'John Coltrane', 'John Scofield', 'John Zorn', 'Ken Vandermark',
    'King Crimson', 'Led Zeppelin', 'Mahavishnu Orchestra', 'Miles Davis', 'Nirvana',
    'Ornette Coleman', 'Paul McCartney', 'Pearl Jam', 'Pink Floyd', 'Police',
    'Porcupine Tree', 'Radiohead', 'Red Hot Chili Peppers', 'Return to Forever', 'Rush',
    'Smashing Pumpkins', 'Soft Machine', 'Soundgarden', 'Stone Temple Pilots', 'System of a Down',
    'Thelonious Monk', 'Weather Report', 'Wings', 'Yes'
]
```

### Step 4.3: Create the ListboxChooser Instance

We will create an instance of `ListboxChooser` and pass the artist names to it.

```python
listbox_chooser = ListboxChooser('Choose Artist/s', {name: name for name in artist_names})
```

### Step 4.4: Generate the Graph Models

We will generate the GraphModel for the selected artists.
First creating a GraphModel for each artist and then combining them into a single model.
In this case, we will use the `reduce` function from the `functools` module to combine the models using the
`operator.add` function. It leverages the GrapModel support of the + operation.

```python
models = (music_graph_model(a, 2) for _, a in listbox_chooser.get_choices())
model = reduce(operator.add, models)
```

### Step 4.5: Materialize the Graph

Using the `GraphQLBuilder` we generate a GraphQL Schema (i.e. strawberry-graphql schema)
and use the `graphql.server` function to create and run the GraphQL server.

```python
# Use the GraphQLBuilder Builder
builder = graphinate.builders.GraphQLBuilder(graph_model)

# build the strawberry-graphql schema
schema = builder.build()

# plot the graph using matplotlib
graphinate.graphql.server(schema)
```

### Step 4.6: Putting everything together

```python
if __name__ == '__main__':
    from gui import ListboxChooser

    artist_names = [
        'Alice in Chains', 'Beatles', 'Caravan', 'Charles Mingus', 'Dave Brubeck',
        'Dave Douglas', 'David Bowie', 'Deep Purple', 'Dire Straits', 'Emerson, Lake & Palmer',
        'Foo Fighters', 'Frank Zappa', 'Genesis', 'Gentle Giant', 'Herbie Hancock',
        'Jethro Tull', 'John Coltrane', 'John Scofield', 'John Zorn', 'Ken Vandermark',
        'King Crimson', 'Led Zeppelin', 'Mahavishnu Orchestra', 'Miles Davis', 'Nirvana',
        'Ornette Coleman', 'Paul McCartney', 'Pearl Jam', 'Pink Floyd', 'Police',
        'Porcupine Tree', 'Radiohead', 'Red Hot Chili Peppers', 'Return to Forever', 'Rush',
        'Smashing Pumpkins', 'Soft Machine', 'Soundgarden', 'Stone Temple Pilots', 'System of a Down',
        'Thelonious Monk', 'Weather Report', 'Wings', 'Yes'
    ]

    listbox_chooser = ListboxChooser('Choose Artist/s', {name: name for name in artist_names})

    models = (music_graph_model(a, 2) for _, a in listbox_chooser.get_choices())
    model = reduce(operator.add, models)

    # Use the GraphQLBuilder Builder
    builder = graphinate.builders.GraphQLBuilder(graph_model)

    # build the strawberry-graphql schema
    schema = builder.build()

    # plot the graph using matplotlib
    graphinate.server(schema)
```

## Step 5: Run the Script

Combine the code from steps 3 and step 4 into a single script `music_artists.py`.

Finally, run the script to start the application and create the music artist graph.

A preloaded diskcache cache is included in the repository, so you can run the script without having to wait for the API
calls.

```shell
python music_artists.py
```

This will open a GUI window where you can select artists and generate the graph model.
