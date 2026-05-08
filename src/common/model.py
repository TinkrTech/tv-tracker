from datetime import date
import textwrap
from sqlmodel import SQLModel, Field
from typing import Optional
from dataclasses import dataclass


@dataclass
class AllSeriesData:
    series: Series
    seasons: list[Season]
    episodes: list[Episode]
    season_episodes: list[SeasonEpisode]


class Episode(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    title: str
    overview: Optional[str]
    aired: Optional[date]


# Episodes are many-to-many
class SeasonEpisode(SQLModel, table=True):
    season_id: int = Field(primary_key=True, foreign_key="season.tvdb_id")
    episode_id: int = Field(primary_key=True, foreign_key="episode.tvdb_id")

    number: int


class Season(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    number: int
    order: str
    series_id: int = Field(foreign_key="series.tvdb_id")


class Series(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    title: str
    year: str
    last_aired: date
    retrieved: date
    keep_updated: bool

    def __str__(self) -> str:
        result = textwrap.dedent(f"""\
            ["{self.title} ({self.year})"]
            tvdb_id = {self.tvdb_id}
            title = "{self.title}"
            year = "{self.year}"
            last_aired = "{self.last_aired}"
            retrieved = "{self.retrieved}"
            keep_updated = {str(self.keep_updated).lower()}
        """).strip()
        return result

    def stub_info(self) -> str:
        return f"{self.title} ({self.year})"

    def full_info(self) -> str:
        no_header_lines = str(self).split('\n')[1:]
        return "\n".join(no_header_lines)


class SeriesConfig(SQLModel, table=True):
    series_id: int = Field(foreign_key="series.tvdb_id", primary_key=True)
    order: str = Field(default="official")
    language: str = Field(default="eng", min_length=3, max_length=3, nullable=True)
