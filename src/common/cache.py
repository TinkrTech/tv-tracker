import tomllib
from os import PathLike
from typing import Iterable

from common.model import Series


PATH = None
__CACHE: list[Series] = None


def load() -> list[Series]:
    global PATH, __CACHE

    if __CACHE is None:
        with open(PATH, 'rb') as cfg:
            entries = tomllib.load(cfg)

        __CACHE = [Series(**entry) for entry in entries.values()]

    return __CACHE


def has(tvdb_id: int) -> bool:
    global PATH, __CACHE
    assert isinstance(tvdb_id, int)

    load()

    cached_ids = [cached.tvdb_id for cached in __CACHE]
    return tvdb_id in cached_ids


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