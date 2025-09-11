from datetime import date
import textwrap

from dataclasses import dataclass, field
import dataclasses

from typing import Optional, Self


@dataclass(slots=True, frozen=True)
class Episode:
    tvdb_id: int
    title: str
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

    def full_info(self) -> str:
        no_header_lines = str(self).split('\n')[1:]
        return "\n".join(no_header_lines)

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

    def using(self, **kwargs) -> Self:
        fields = dataclasses.asdict(self)
        fields.update(kwargs)
        return Series(**fields)
