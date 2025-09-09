import tomllib
from os import PathLike
from typing import Iterable

from common.model import Series


__CACHE: list[Series] = None


def load(path: PathLike) -> list[Series]:
    global __CACHE
    with open(path, 'rb') as cfg:
        entries = tomllib.load(cfg)

    __CACHE = [Series(**entry) for entry in entries.values()]
    return __CACHE


def has(path: PathLike, tvdb_id: int) -> bool:
    global __CACHE
    assert isinstance(tvdb_id, int)

    if __CACHE is None:
        load(path)

    cached_ids = [tvdb_id for cached in __CACHE]
    return tvdb_id in cached_ids


def add(path: PathLike, item: Series) -> None:
    global __CACHE
    if has(path, item.tvdb_id):
        print(f"WARNING: \"{item.stub_info()}\" is already being tracked. Skipping...")
        return

    with open(path, 'a') as cfg:
        cfg.write(str(item) + "\n\n")

    __CACHE.append(item)


def update(path: PathLike, updated: Iterable[Series]) -> None:
    global __CACHE
    __CACHE = list(updated)

    with open(path, "w") as cfg:
        for item in updated:
            cfg.write(str(item) + "\n\n")