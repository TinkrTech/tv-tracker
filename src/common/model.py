from datetime import date
import textwrap
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


# Episodes are many-to-many
class SeasonEpisode(SQLModel, table=True):
    season_id: int = Field(primary_key=True, foreign_key="season.tvdb_id", ondelete="CASCADE")
    episode_id: int = Field(primary_key=True, foreign_key="episode.tvdb_id", ondelete="CASCADE")
    number: int

    season: 'Season' = Relationship(back_populates="season_episodes")
    episode: 'Episode' = Relationship(back_populates="season_episodes")


class Episode(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    title: str
    overview: Optional[str]
    aired: Optional[date]

    season_episodes: list[SeasonEpisode] = Relationship(
        back_populates="episode",
        cascade_delete=True,
    )


class Season(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    number: int
    order: str
    series_id: int = Field(foreign_key="series.tvdb_id", ondelete="CASCADE")

    season_episodes: list[SeasonEpisode] = Relationship(
        back_populates="season",
        cascade_delete=True,
    )


class SeriesConfig(SQLModel, table=True):
    series_id: int = Field(
        primary_key=True,
        foreign_key="series.tvdb_id",
        ondelete="CASCADE",
    )
    order: str = Field(default="official")
    language: str = Field(default="eng", min_length=3, max_length=3)

    series: 'Series' = Relationship(back_populates="config")


class Series(SQLModel, table=True):
    tvdb_id: int = Field(primary_key=True)
    title: str
    year: str
    last_aired: date
    retrieved: date
    keep_updated: bool

    seasons: list[Season] = Relationship(
        cascade_delete=True,
    )

    config: SeriesConfig = Relationship(
        back_populates="series",
        cascade_delete=True,
    )

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
