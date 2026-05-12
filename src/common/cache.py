import logging as log
from pathlib import Path

from collections.abc import Iterable, Iterator

from sqlmodel import SQLModel, select, delete as delete_, or_, and_, func, text as text_
import sqlmodel
from sqlalchemy.orm import selectinload

from common.model import Series, Season, Episode, SeasonEpisode, AllSeriesData, SeriesConfig


__ENGINE = None
type SeriesId = type(Series.tvdb_id)


def _result_of(statement):
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        return session.exec(statement).all()


def initialize(path: Path) -> None:
    global __ENGINE

    if __ENGINE is not None:
        return

    if path == '':
        log.warn("Trying to initialize database with no path. NOTHING FROM THIS SESSION WILL BE SAVED!")
        path = ":memory:"
    uri = f"sqlite:///{path}"

    __ENGINE = sqlmodel.create_engine(uri)

    with sqlmodel.Session(__ENGINE) as session:
        session.exec(text_("PRAGMA foreign_keys = ON"))
        session.commit()

    SQLModel.metadata.create_all(__ENGINE)
    log.debug(f"Loaded engine from '{uri}'")


def migrate_toml(old: Path) -> None:
    import tomllib
    from datetime import date
    assert old.exists()
    assert old.suffix == ".toml"
    assert __ENGINE != None

    def load_old() -> list[Series]:
        with open(old, 'rb') as cfg:
            entries = tomllib.load(cfg)
        for key, value in entries.items():
            entries[key]["last_aired"] = date.fromisoformat(value["last_aired"])
            entries[key]["retrieved"] = date.fromisoformat(value["retrieved"])
        return [Series(**entry) for entry in entries.values()]

    items = load_old()
    log.debug(f"Loaded {len(items)} items")

    with sqlmodel.Session(__ENGINE) as session:
        session.add_all(items)
        session.commit()
        statement = select(Series)
        count_added = len(session.exec(statement).all())

    log.debug(f"Added {count_added} items")


def has(tvdb_id: int) -> bool:
    all_matching = select(Series)\
        .where(Series.tvdb_id == tvdb_id)
    return len(_result_of(all_matching)) != 0


def _where_titles_match(titles: str|Iterable[str], strict: bool=True):
    if not isinstance(titles, list):
        titles = [titles]

    titles = map(lambda x: x.lower(), titles)

    if strict:
        titles_match = func.lower(Series.title).in_(titles)
    else:
        titles_match = or_(
            *(
                func.lower(Series.title).like(f"%{title}%")
                for title in titles
            )
        )
    return titles_match


def find(titles: str|list[str], *, strict:bool=False, query_options=None) -> list[Series]:
    global __ENGINE

    if query_options is None:
        query_options = []

    results = _result_of(
        select(Series)\
        .where(_where_titles_match(titles, strict=strict))\
        .order_by(func.char_length(Series.title))
        .options(*query_options)
    )

    return results

def series_orders(series_id: SeriesId, *, with_count: bool = False):
    cols = Season.order
    if with_count:
        cols = Season.order, func.count(Season.order)

    query = select(cols)\
        .where(Season.series_id == series_id)\
        .group_by(Season.order)\
        .order_by(Season.order)
    return _result_of(query)


def list_all[T](t: T = Series) -> list[T]:
    return _result_of(select(t))


def fix_configs() -> None:
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        all_series = session.exec(select(Series)).all()

        for series in all_series:
            if not series.config:
                config = SeriesConfig(series_id=series.tvdb_id, series=series)
                session.add(config)
        session.commit()


def list_seasons(series_id: SeriesId, *, order: str, season_number: int|None=None) -> list[Season]:
    where = and_(Season.series_id == series_id, Season.order == order)
    if season_number is not None:
        where = and_(where, Season.number == season_number)
    else:
        where = and_(where, Season.number != 0)

    query = select(Season)\
        .where(where)\
        .order_by(Season.number)\
        .options(
            selectinload(Season.season_episodes)\
            .selectinload(SeasonEpisode.episode)
        )

    return _result_of(query)


def add(items: Iterable[SQLModel]) -> None:
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        session.add_all(items)
        session.commit()


def update(items: SQLModel|Iterable[SQLModel]) -> None:
    from typing import reveal_type
    global __ENGINE

    if isinstance(items, SQLModel):
        items = [items]

    with sqlmodel.Session(__ENGINE) as session:
        for item in items:
            session.merge(item)
        session.commit()


def delete(deleted: Iterable[SeriesId]) -> None:
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        deletions = delete_(Series)\
            .where(Series.tvdb_id.in_(deleted))
        session.exec(deletions)

        orphans = select(Episode)\
            .where(~Episode.season_episodes.any())

        for orphan in session.exec(orphans).all():
            session.delete(orphan)
        session.commit()
