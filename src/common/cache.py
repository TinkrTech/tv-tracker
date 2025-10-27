import tomllib
from collections.abc import Iterable, Iterator

from common.model import Series


PATH: str = ''
__CACHE: list[Series] = []
__LOADED = False


def load() -> list[Series]:
    global PATH, __CACHE, __LOADED
    assert PATH != ''

    if not __LOADED:
        with open(PATH, 'rb') as cfg:
            entries = tomllib.load(cfg)

        __CACHE = [Series(**entry) for entry in entries.values()]
        __LOADED = True
    return __CACHE


def has(tvdb_id: int) -> bool:
    global __CACHE
    assert isinstance(tvdb_id, int)

    load()

    cached_ids = [cached.tvdb_id for cached in __CACHE]
    return tvdb_id in cached_ids


def find(titles: str|list[str], *, strict=False) -> Iterator[Series]:
    global __CACHE
    assert titles is not None

    load()

    if not isinstance(titles, list):
        titles = [titles]

    if strict:
        matches = lambda x, y: x == y
    else:
        matches = lambda x, y: x in y

    for title in titles:
        for series in __CACHE:
            if matches(title.lower(), series.title.lower()):
                yield series


def add(item: Series) -> None:
    global PATH, __CACHE

    if has(item.tvdb_id):
        print(f"WARNING: \"{item.stub_info()}\" is already being tracked. Skipping...")
        return

    with open(PATH, 'a') as cfg:
        cfg.write(str(item) + "\n\n")

    __CACHE.append(item)


def update(updated: Iterable[Series]) -> None:
    global PATH, __CACHE

    with open(PATH, "w") as cfg:
        for item in updated:
            cfg.write(str(item) + "\n\n")

    __CACHE = list(updated)