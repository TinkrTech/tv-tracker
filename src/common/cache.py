# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>

import logging as log
from pathlib import Path

import typing
from typing import Iterable, Sequence

import sqlmodel
from sqlmodel import SQLModel, select, delete as delete_, or_, and_, func, text as text_
from sqlmodel.sql.expression import SelectOfScalar as Select, ColumnElement
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import QueryableAttribute

from common.model import Series, Season, Episode, SeasonEpisode, SeriesConfig


__ENGINE = None
type SeriesId = int
type Column = ColumnElement
type Where = bool|ColumnElement[bool]


def t_col[T](val: T) -> ColumnElement[T]:
    """Coerce type into a ColumnElement"""
    return typing.cast(ColumnElement[T], val)


def t_attr[T](val: T) -> QueryableAttribute[T]:
    """Coerce type into a QueryableAttribute"""
    return typing.cast(QueryableAttribute[T], val)


def initialize(path: Path|None) -> None:
    global __ENGINE

    if __ENGINE is not None:
        return

    if path is None:
        log.warn("Trying to initialize database with no path. NOTHING FROM THIS SESSION WILL BE SAVED!")
        uri = "sqlite:///:memory:"
    else:
        uri = f"sqlite:///{path}"

    __ENGINE = sqlmodel.create_engine(uri)

    with sqlmodel.Session(__ENGINE) as session:
        session.execute(text_("PRAGMA foreign_keys = ON"))
        session.commit()

    SQLModel.metadata.create_all(__ENGINE)
    log.debug(f"Loaded engine from '{uri}'")


def result_of[T](
        selection: Select[T],
        *,
        where: Where|Iterable[Where]=True,
        order_by: Column|None=None
    ) -> Sequence[T]:
    global __ENGINE

    if isinstance(where, Iterable) and not isinstance(where, ClauseElement):
        where = and_(*where)

    query = selection\
        .where(where)\
        .order_by(order_by)

    with sqlmodel.Session(__ENGINE) as session:
        return session.exec(query).all()


def select_series() -> Select[Series]:
    return select(Series).options(
        selectinload(t_attr(Series.config))
    )


def select_seasons(*, series_id: SeriesId|None = None) -> Select[Season]:
    return select(Season)\
        .where(Season.series_id == series_id)\
        .options(
            selectinload(t_attr(Season.season_episodes))\
            .selectinload(t_attr(SeasonEpisode.episode))
        )


def migrate_toml(old: Path) -> None:
    import tomllib
    from datetime import date

    assert old.exists()
    assert old.suffix == ".toml"
    assert __ENGINE != None

    def load_one(entry: dict) -> Series:
        config = SeriesConfig(
            series_id=entry["tvdb_id"],
            order=entry.get("use_order"),
            language=entry.get("use_language"),
        )
        series = Series(
            tvdb_id=entry["tvdb_id"],
            title=entry["title"],
            year=entry["year"],
            last_aired=date.fromisoformat(entry["last_aired"]),
            retrieved=date.fromisoformat(entry["retrieved"]),
            keep_updated=entry["keep_updated"],
            config=config,
        )
        return series

    with open(old, "rb") as cfg:
        entries = tomllib.load(cfg)
        items = [load_one(entry) for entry in entries.values()]

    log.debug(f"Loaded {len(items)} items")

    with sqlmodel.Session(__ENGINE) as session:
        session.add_all(items)
        session.commit()

    count_added = len(result_of(select_series()))
    log.debug(f"Added {count_added} items")


def has(tvdb_id: int) -> bool:
    result = result_of(
        select_series(),
        where=(Series.tvdb_id == tvdb_id)
    )
    return len(result) != 0


def _titles_match(titles: str|Iterable[str], strict: bool=True) -> Where:
    if isinstance(titles, str):
        titles = [titles]

    if strict:
        titles_match: ColumnElement = func.lower(Series.title)\
            .in_(
                title.lower()
                for title in titles
            )
    else:
        titles_match = or_(
            *(
                Series.title.ilike(f"%{title}%")
                for title in titles
            )
        )
    return titles_match


def find(titles: str|list[str], *, strict:bool=False) -> Sequence[Series]:
    return result_of(
        select_series(),
        where=_titles_match(titles, strict=strict),
        order_by=t_col(Series.title)
    )


def series_orders(series_id: SeriesId, *, with_count: bool = False):
    if with_count:
        cols = (Season.order, func.count(t_col(Season.order)))
    else:
        cols = (Season.order)

    query = select(cols)\
        .where(Season.series_id == series_id)\
        .group_by(Season.order)\
        .order_by(Season.order)
    return result_of(query)


def is_valid_order(series: Series, order: str) -> bool:
    orders = series_orders(series.tvdb_id)
    is_valid = order in orders
    if not is_valid:
        log.warning(f"Supported orders for \"{series.stub_info()}\" are {orders}")
    return is_valid


def fix_configs() -> None:
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        all_series = session.exec(select_series()).all()

        for series in all_series:
            if not series.config:
                config = SeriesConfig(series_id=series.tvdb_id, series=series)
                session.add(config)
        session.commit()


def add(items: SQLModel|Iterable[SQLModel]) -> None:
    global __ENGINE

    if isinstance(items, SQLModel):
        items = [items]

    with sqlmodel.Session(__ENGINE) as session:
        session.add_all(items)
        session.commit()


def update(items: SQLModel|Iterable[SQLModel]) -> None:
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
            .where(t_col(Series.tvdb_id).in_(deleted))
        session.exec(deletions)

        orphans = select(Episode)\
            .where(~t_col(Episode.season_episodes).any())

        for orphan in session.exec(orphans).all():
            session.delete(orphan)
        session.commit()
