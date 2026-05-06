import logging as log
from pathlib import Path

from collections.abc import Iterable, Iterator

from sqlmodel import SQLModel, Field, select, or_, and_

import sqlmodel

from common.model import Series


__ENGINE = None


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
    print(repr(items[0].last_aired))
    log.debug(f"Loaded {len(items)} items")

    with sqlmodel.Session(__ENGINE) as session:
        session.add_all(items)
        session.commit()
        statement = select(Series)
        count_added = len(session.exec(statement).all())

    log.debug(f"Added {count_added} items")


def add(item: Series) -> None:
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        if has(item.tvdb_id):
            log.warn(f"'{item.stub_info()}' is already being tracked. Skipping...")
            return

        session.add(item)
        session.commit()


def has(tvdb_id: int) -> bool:
    all_matching = select(Series)\
        .where(Series.tvdb_id == tvdb_id)
    return len(_result_of(all_matching)) != 0


def find(titles: str|list[str], *, strict=False) -> Iterator[Series]:
    global __ENGINE

    assert titles is not None

    if not isinstance(titles, list):
        titles = [titles]

    titles = map(lambda x: x.lower(), titles)

    if strict:
        titles_match = Series.title.lower().in_(titles)
    else:
        titles_match = or_(
            *(title in Series.title.lower() for title in titles)
        )

    results = _result_of(
        select(Series)\
        .where(titles_match)\
        .order_by(len(Series.title))
    )

    for result in results:
        yield result


def update(updated: Iterable[Series]) -> None:
    global __ENGINE

    with sqlmodel.Session(__ENGINE) as session:
        session.bulk_update_mappings(
            Series,
            (series.model_dump(exclude_unset=True) for series in updated)
        )
        session.commit()
