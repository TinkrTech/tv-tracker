import tomllib
from datetime import date
from os import PathLike
import textwrap

from dataclasses import dataclass, field
from typing import Optional, Self


@dataclass(slots=True, frozen=True)
class Episode:
    tvdb_id: int
    name: str
    number: int
    aired: Optional[date]


@dataclass(slots=True, frozen=True)
class Season:
    tvdb_id: int
    number: int
    order: str
    episodes: list[Episode] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class Series:
    tvdb_id: int
    title: str
    year: str
    last_aired: date
    retrieved: date
    keep_updated: bool
    use_order: str
    orders: list[str]
    seasons: list[Season] = field(default_factory=list)
    season_count: Optional[int] = None

    def __str__(self) -> str:
        return textwrap.dedent(f"""\
            ["{self.title} ({self.year})"]
            tvdb_id = {self.tvdb_id}
            title = "{self.title}"
            year = "{self.year}"
            season_count = {self.get_season_count()}
            last_aired = "{self.last_aired}"
            retrieved = "{self.retrieved}"
            keep_updated = {str(self.keep_updated).lower()}
            orders = {self.orders}
            use_order = "{self.use_order}"
        """).strip()

    def stub_info(self) -> str:
        return f"{self.title} ({self.year})"

    def get_season_count(self) -> int:
        if self.season_count is None:
            seasons = [
                season for season in self.seasons
                if season.number != 0
                and season.order == self.use_order
                and len(season.episodes) != 0
            ]
            return len(seasons)
        else:
            return self.season_count


def from_config(config_path: PathLike) -> list[Series]:
    with open(config_path, 'rb') as cfg:
        entries = tomllib.load(cfg)
    return [Series(**entry) for entry in entries.values()]


def is_in_config(config_path: PathLike, tvdb_id: int) -> bool:
    assert isinstance(tvdb_id, int)

    cached_ids = [tvdb_id for cached in from_config(config_path)]
    return tvdb_id in cached_ids


def add_to_config(config_path: PathLike, item: Series) -> None:
    if is_in_config(config_path, item.tvdb_id):
        print(f"WARNING: \"{item.stub_info()}\" is already being tracked. Skipping...")
        return

    with open(config_path, 'a') as cfg:
        cfg.write(str(item) + "\n\n")


def update_config(config_path: PathLike, updated: list[Series]) -> None:
    with open(config_path, "w") as cfg:
        for item in updated:
            cfg.write(str(item) + "\n\n")