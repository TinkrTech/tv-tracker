# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
from pytest import MonkeyPatch

import datetime
from common.provider import TVDBProvider, SearchResult
from common import model
from common import cache

@pytest.fixture
def provider() -> TVDBProvider:
    return TVDBProvider("dummy_token")


def mock_search_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "country": "usa",
                "id": "series-371980",
                "image_url": "https://artworks.thetvdb.com/banners/v4/series/371980/posters/621096b26f0e2.jpg",
                "name": "Severance",
                "first_air_time": "2022-02-18",
                "overview": "Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives. When a mysterious colleague appears outside of work, it begins a journey to discover the truth about their jobs.",
                "primary_language": "eng",
                "primary_type": "series",
                "status": "Continuing",
                "type": "series",
                "tvdb_id": "371980",
                "year": "2022",
                "slug": "severance",
                "overviews": {
                    "deu": "Mark (Adam Scott) ist ein neuer Mitarbeiter bei Lumen Industries. Dort will man die vielbeschworene Work-Life-Balance auf ein neues Niveau bringen. Doch Marks d\u00fcstere Vergangenheit behindert seinen Neuanfang. (Text: RD)",
                    "eng": "Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives. When a mysterious colleague appears outside of work, it begins a journey to discover the truth about their jobs.",
                    "fra": "Mark dirige une \u00e9quipe d'employ\u00e9s de bureau dont les souvenirs ont \u00e9t\u00e9 scind\u00e9s chirurgicalement en fonction de leur vie professionnelle et de leur vie priv\u00e9e. L'irruption d'un myst\u00e9rieux coll\u00e8gue en dehors du bureau enclenche une longue qu\u00eate de v\u00e9rit\u00e9 sur leur travail.",
                    "swe": "Mark leder ett team av kontorsarbetare vars minnen har splittrats kirurgiskt mellan deras arbetsliv och privatliv. N\u00e4r en mystisk kollega dyker upp utanf\u00f6r arbetstid p\u00e5b\u00f6rjas en resa f\u00f6r att uppt\u00e4cka sanningen om deras jobb.",
                },
                "translations": {
                    "deu": "German-Severance",
                    "eng": "English-Severance",
                    "fra": "French-Severance",
                    "swe": "Swedish-Severance",
                },
            },
            {
                "objectID": "series-318009",
                "country": "nor",
                "id": "series-318009",
                "image_url": "https://artworks.thetvdb.com/banners/posters/318009-2.jpg",
                "name": "Norsemen",
                "first_air_time": "2016-10-21",
                "overview": "An epic sitcom set in the Viking Age. The residents of an 8th-century Viking village experience political rivalry, social change and innovations that upend their culture and way of life.",
                "primary_language": "eng",
                "primary_type": "series",
                "status": "Ended",
                "type": "series",
                "tvdb_id": "318009",
                "year": "2016",
                "slug": "norsemen",
                "overviews": {
                    "deu": "Die Wikinger von Norheim haben im Jahr 790 n. Chr. mit Pl\u00fcnderungen, Versklavungen und gewaltt\u00e4tigen Probleml\u00f6sungen alle H\u00e4nde voll zu tun.",
                    "eng": "An epic sitcom set in the Viking Age. The residents of an 8th-century Viking village experience political rivalry, social change and innovations that upend their culture and way of life.",
                    "fra": "Rivalit\u00e9s politiques, changements sociaux et innovations bouleversent la culture et le mode de vie des r\u00e9sidents d'un village viking du VIIIe si\u00e8cle.",
                    "nor": "Vikingane er en episk og humorserie satt i vikingtiden. \u00c5ret er 790 og i seks episoder f\u00f8lger vi hverdagslivet til vikingene i landsbyen Norheim. Mellom maktkamp, tokt og slag i en t\u00f8ff tid byr livet p\u00e5 gode vennskap, fest og kj\u00e6rlighet, samtidig som de blir utfordret av nye moderne trender med innf\u00f8ring av myke verdier og kunst, krangling og sjalusi, samlivsproblemer og tr\u00f8blete s\u00f8skenforhold vi kjenner fra moderne tid.",
                },
                "translations": {
                    "deu": "German-Norsemen",
                    "eng": "English-Norsemen",
                    "fra": "French-Norsemen",
                    "nor": "Vikingane",
                },
                "network": "NRK1",
            },
        ],
    }

def mock_series_response() -> dict:
    return {
        "status": "success",
        "data": {
            "id": 78874,
            "name": "Firefly",
            "slug": "firefly",
            "nameTranslations": ["deu","eng","fra","swe",],
            "overviewTranslations": ["deu","eng","fra","swe",],
            "firstAired": "2002-09-20",
            "lastAired": "2003-07-28",
            "nextAired": "",
            "status": {
                "id": 2,
                "name": "Ended",
                "recordType": "series",
                "keepUpdated": False
            },
            "originalCountry": "usa",
            "originalLanguage": "eng",
            "defaultSeasonType": 1,
            "isOrderRandomized": False,
            "lastUpdated": "2026-05-17 13:24:13",
            "averageRuntime": 48,
            "episodes": None,
            "overview": "In the far-distant future, Captain Malcolm \"Mal\" Reynolds is a renegade former brown-coat sergeant, now turned smuggler & rogue, who is the commander of a small spacecraft, with a loyal hand-picked crew made up of the first mate, Zoe Warren; the pilot Hoban \"Wash\" Washburn; the gung-ho grunt Jayne Cobb; the engineer Kaylee Frye; the fugitives Dr. Simon Tam and his psychic sister River. Together, they travel the far reaches of space in search of food, money, and anything to live on.",
            "year": "2002",
            "seasons": [
            {
                "id": 15791,
                "seriesId": 78874,
                "type": {
                    "id": 1,
                    "name": "Aired Order",
                    "type": "official",
                    "alternateName": "Aired Order"
                },
                "number": 1,
                "nameTranslations": [],
                "overviewTranslations": ["eng,fra"],
                "lastUpdated": "2026-03-02 18:42:16"
            },
            {
                "id": 1775413,
                "seriesId": 78874,
                "type": {
                "id": 3,
                    "name": "Absolute Order",
                    "type": "absolute",
                    "alternateName": None
                },
                "number": 1,
                "nameTranslations": [],
                "overviewTranslations": [],
                "lastUpdated": "2026-03-02 18:42:16"
            },
            {
                "id": 1775414,
                "seriesId": 78874,
                "type": {
                    "id": 2,
                    "name": "DVD Order",
                    "type": "dvd",
                    "alternateName": None
                },
                "number": 1,
                "nameTranslations": [],
                "overviewTranslations": [],
                "lastUpdated": "2026-03-02 18:42:16"
            },
            {
                "id": 1887664,
                "seriesId": 78874,
                "type": {
                "id": 2,
                    "name": "DVD Order",
                    "type": "dvd",
                    "alternateName": None
                },
                "number": 0,
                "nameTranslations": [],
                "overviewTranslations": [],
                "lastUpdated": "2022-09-27 22:55:28"
            }
            ],
            "seasonTypes": [
                {
                    "id": 1,
                    "name": "Aired Order",
                    "type": "official",
                    "alternateName": "Aired Order"
                },
                {
                    "id": 2,
                    "name": "DVD Order",
                    "type": "dvd",
                    "alternateName": None
                },
                {
                    "id": 3,
                    "name": "Absolute Order",
                    "type": "absolute",
                    "alternateName": None
                }
            ]
        }
    }

def mock_episode_response(order: str, language: str) -> dict:
    return {
        "status": "success",
        "data": {
            "id": 78874,
            "name": f"{language}-Firefly",
            "slug": "firefly",
            "firstAired": "2002-09-20",
            "lastAired": "2003-07-28",
            "nextAired": "",
            "score": 156079,
            "status": {
                "id": 2,
                "name": "Ended",
                "recordType": "series",
                "keepUpdated": False
            },
            "originalCountry": "usa",
            "originalLanguage": "eng",
            "defaultSeasonType": 1,
            "isOrderRandomized": False,
            "averageRuntime": 48,
            "episodes": [
                {
                    "id": hash(order),
                    "seriesId": 78874,
                    "name": f"{order}-{language}-Episode 1",
                    "aired": "2002-12-20",
                    "runtime": 87,
                    "overview": f"Overview in {language}",
                    "number": 1,
                    "absoluteNumber": 1,
                    "seasonNumber": 1
                },
            ],
            "overview": f"Series Overview in {language}",
            "year": "2002"
        },
        "links": {
            "prev": None,
            "self": "https://api4.thetvdb.com/v4/series/78874/episodes/dvd/eng?page=0",
            "next": None,
            "total_items": 17,
            "page_size": 500
        }
    }

def mock_fetch_series_responses(endpoint: str, *args, **kwargs):
    if endpoint.endswith("extended"):
        return mock_series_response()
    elif "translations" in endpoint:
        lang = endpoint.split("/")[-1]
        return {"data": {"name": f"{lang}-Firefly"}}
    else:
        order = endpoint.split("/")[-2]
        lang = endpoint.split("/")[-1]
        return mock_episode_response(order, lang)

def test_search_by_title_only_query(monkeypatch: MonkeyPatch, provider: TVDBProvider) -> None:
    monkeypatch.setattr(cache, "has", lambda x: False)
    monkeypatch.setattr(provider, "_make_request", lambda *args, **kwargs: mock_search_response())

    query = {"query": "severance", "year": None, "language": None}
    actual = provider.search(query)

    expected = [
        SearchResult(
            tvdb_id=371980,
            title="English-Severance",
            original_title="Severance",
            language="eng",
            year="2022",
            synopsis="Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives. When a mysterious colleague appears outside of work, it begins a journey to discover the truth about their jobs.",
            is_tracked=False
        ),
        SearchResult(
            tvdb_id=318009,
            title="English-Norsemen",
            original_title="Norsemen",
            language="eng",
            year="2016",
            synopsis="An epic sitcom set in the Viking Age. The residents of an 8th-century Viking village experience political rivalry, social change and innovations that upend their culture and way of life.",
            is_tracked=False
        ),
    ]

    assert actual == expected

def test_search_by_title_with_valid_translation(monkeypatch: MonkeyPatch, provider: TVDBProvider) -> None:
    monkeypatch.setattr(cache, "has", lambda x: False)
    monkeypatch.setattr(provider, "_make_request", lambda *args, **kwargs: mock_search_response())

    query = {"query": "severance", "year": None, "language": None}
    actual = provider.search(query, translate="fra")
    expected = [
            SearchResult(
            tvdb_id=371980,
            title="French-Severance",
            original_title="Severance",
            language="eng",
            year="2022",
            synopsis="Mark dirige une \u00e9quipe d'employ\u00e9s de bureau dont les souvenirs ont \u00e9t\u00e9 scind\u00e9s chirurgicalement en fonction de leur vie professionnelle et de leur vie priv\u00e9e. L'irruption d'un myst\u00e9rieux coll\u00e8gue en dehors du bureau enclenche une longue qu\u00eate de v\u00e9rit\u00e9 sur leur travail.",
            is_tracked=False
        ),
        SearchResult(
            tvdb_id=318009,
            title="French-Norsemen",
            original_title="Norsemen",
            language="eng",
            year="2016",
            synopsis="Rivalit\u00e9s politiques, changements sociaux et innovations bouleversent la culture et le mode de vie des r\u00e9sidents d'un village viking du VIIIe si\u00e8cle.",
            is_tracked=False
        ),
    ]

    assert actual == expected

def test_search_by_title_with_invalid_translation(monkeypatch: MonkeyPatch, provider: TVDBProvider) -> None:
    monkeypatch.setattr(cache, "has", lambda x: False)
    monkeypatch.setattr(provider, "_make_request", lambda *args, **kwargs: mock_search_response())

    query = {"query": "severance", "year": None, "language": None}
    actual = provider.search(query, translate="nor")

    expected = [
        SearchResult(
            tvdb_id=371980,
            title="Severance",
            original_title="Severance",
            language="eng",
            year="2022",
            synopsis="Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives. When a mysterious colleague appears outside of work, it begins a journey to discover the truth about their jobs.",
            is_tracked=False
        ),
        SearchResult(
            tvdb_id=318009,
            title="Vikingane",
            original_title="Norsemen",
            language="eng",
            year="2016",
            synopsis="Vikingane er en episk og humorserie satt i vikingtiden. \u00c5ret er 790 og i seks episoder f\u00f8lger vi hverdagslivet til vikingene i landsbyen Norheim. Mellom maktkamp, tokt og slag i en t\u00f8ff tid byr livet p\u00e5 gode vennskap, fest og kj\u00e6rlighet, samtidig som de blir utfordret av nye moderne trender med innf\u00f8ring av myke verdier og kunst, krangling og sjalusi, samlivsproblemer og tr\u00f8blete s\u00f8skenforhold vi kjenner fra moderne tid.",
            is_tracked=False
        ),
    ]

    assert actual == expected


def test_fetch_series_valid_order(monkeypatch: MonkeyPatch, provider: TVDBProvider) -> None:
    monkeypatch.setattr(provider, "_make_request", mock_fetch_series_responses)

    config = model.SeriesConfig(series_id=78874, order="dvd", language="eng")
    actual = provider.fetch_series(config)

    expected_config = config

    expected_seasons = []
    expected = model.Series(
        tvdb_id=78874,
        title='eng-Firefly',
        year='2002',
        last_aired=datetime.date(2003, 7, 28),
        retrieved=datetime.date(2026, 6, 8),
        keep_updated=False,
    )


    assert actual == expected
    assert actual.config == expected.config
    assert actual.seasons == expected.seasons
    for actual_season, expected_season in zip(actual.seasons, expected_seasons):
        assert actual_season.season_episodes == expected_season.season_episodes

    assert actual.seasons.season_episodes


