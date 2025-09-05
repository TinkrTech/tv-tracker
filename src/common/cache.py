import tomllib
from os import PathLike

from common.model import Series


def load(path: PathLike) -> list[Series]:
    with open(path, 'rb') as cfg:
        entries = tomllib.load(cfg)
    return [Series(**entry) for entry in entries.values()]


def has(path: PathLike, tvdb_id: int) -> bool:
    assert isinstance(tvdb_id, int)

    cached_ids = [tvdb_id for cached in load(path)]
    return tvdb_id in cached_ids


def add(path: PathLike, item: Series) -> None:
    if has(path, item.tvdb_id):
        print(f"WARNING: \"{item.stub_info()}\" is already being tracked. Skipping...")
        return

    with open(path, 'a') as cfg:
        cfg.write(str(item) + "\n\n")


def update(path: PathLike, updated: list[Series]) -> None:
    with open(path, "w") as cfg:
        for item in updated:
            cfg.write(str(item) + "\n\n")