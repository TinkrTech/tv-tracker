# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
from pytest import MonkeyPatch
from common.provider import TVDBProvider, SearchResult
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
