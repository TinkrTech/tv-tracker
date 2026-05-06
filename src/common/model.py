from datetime import date
import textwrap
from sqlmodel import SQLModel, Field

from typing import Optional, List


class Episode(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    title: str
    number: int
    aired: Optional[date]

    season_id: int = Field(foreign_key="season.tvdb_id")


class Season(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    number: int
    order_id: int = Field(foreign_key="orders.order_id")
    series_id: int = Field(foreign_key="series.tvdb_id")


class Orders(SQLModel, table=True):
    order_id: int = Field(default=None, primary_key=True)
    name: str


class Series(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    title: str
    year: str
    last_aired: date
    retrieved: date
    keep_updated: bool
    use_order: str

    use_language: Optional[str] = None
    season_count: Optional[int] = None

    def __str__(self) -> str:
        nullable_fields = []
        if self.use_language is not None:
            nullable_fields.append(f'use_language = "{self.use_language}"')

        result = textwrap.dedent(f"""\
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
        if len(nullable_fields) > 0:
            result += "\n" + "\n".join(nullable_fields)
        return result

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

    # def using(self, **kwargs) -> 'Series':
    #     fields = dataclasses.asdict(self)
    #     fields.update(kwargs)
    #     return Series(**fields)
