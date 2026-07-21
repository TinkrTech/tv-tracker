# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
from unittest import mock
from typing import assert_never
import argparse as ap
from datetime import date

from common.provider import SearchResult
from common import model
from common import cache
from common import utils

import track

class Provider:
    def search(self, query: dict, translate: str) -> list[SearchResult]:
        assert_never("provider.search must be overriden by a mock")

    def fetch_series(self, config: model.SeriesConfig) -> model.Series:
        assert_never("provider.fetch_series must be overriden by a mock")

mock_results = [
    {
        "search": SearchResult(123, "Untitled", "Sans-Titre", "2021", "fre", "In a world of titles, be unique.", False),
        "fetch_series": model.Series(tvdb_id=123, title="Untitled", year="2021", last_aired=date(2022, 1, 1), retrieved=date(2022, 2, 2), keep_updated=False),
    },
    {
        "search": SearchResult(111, "Sample Title", "Sample Title", "2003", "eng", "Sample Description", True),
        "fetch_series": model.Series(tvdb_id=111, title="Sample Title",             year="2003", last_aired=date(2012, 2, 2), retrieved=date(2026, 6, 6), keep_updated=False),
    },
    {
        "search": SearchResult(222, "Sample Title: Retconning", "Sample Title: Retconning", "2016", "eng", "Sample Description", False),
        "fetch_series": model.Series(tvdb_id=222, title="Sample Title: Retconning", year="2016", last_aired=date(2017, 3, 3), retrieved=date(2026, 6, 6), keep_updated=True),
    },
]

def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    track.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)


def test_track_with_no_matches():
    provider = Provider()
    provider.search = lambda query, translate: []
    title = "Doesn't Exist"

    track.track(provider, mock_args(title=title))
    # if fetch_series is called then the test will fail on assert_never


@mock.patch.object(utils, 'select')
@mock.patch.object(utils, 'confirm', return_value=True)
@mock.patch.object(cache, 'add')
def test_track_with_one_match(mocked_add, mocked_confirm, mocked_select):
    title = "Untitled"
    sample_data = [mock_results[0]]
    search_data = [data["search"] for data in sample_data]
    series_data = [data["fetch_series"] for data in sample_data]

    provider = Provider()
    provider.search = lambda query, translate: search_data
    provider.fetch_series = lambda config: series_data

    track.track(provider, mock_args(title=title))

    mocked_select.assert_not_called()
    mocked_confirm.assert_called_once()
    mocked_add.assert_called_once_with(series_data)


@mock.patch.object(utils, 'select')
@mock.patch.object(utils, 'confirm')
@mock.patch.object(cache, 'add')
def test_track_with_two_matches(mocked_add, mocked_confirm, mocked_select):
    title = "Sample Title"
    sample_data = mock_results[1:3]
    search_data = [data["search"] for data in sample_data]
    selection = search_data[1]
    series_data = [data["fetch_series"] for data in sample_data][1]

    provider = Provider()
    provider.search = lambda query, translate: search_data
    provider.fetch_series = lambda config: series_data
    mocked_select.return_value = selection

    track.track(provider, mock_args(title=title))

    mocked_select.assert_called_once_with('Select one of the following:\n   * = already tracked', search_data)
    mocked_confirm.assert_not_called()
    mocked_add.assert_called_once_with(series_data)


@mock.patch.object(utils, 'select')
@mock.patch.object(utils, 'confirm')
@mock.patch.object(cache, 'add')
def test_track_with_non_matches(mocked_add, mocked_confirm, mocked_select):
    title = "No Matching"
    sample_data = mock_results
    search_data = [data["search"] for data in sample_data]

    provider = Provider()
    provider.search = lambda query, translate: search_data

    track.track(provider, mock_args(title=title))

    mocked_select.assert_not_called()
    mocked_confirm.assert_not_called()
    mocked_add.assert_not_called()


@mock.patch.object(utils, 'select')
@mock.patch.object(utils, 'confirm')
@mock.patch.object(cache, 'add')
def test_track_with_selecting_already_tracked_item(mocked_add, mocked_confirm, mocked_select):
    title = "Sample Title"
    sample_data = mock_results[1:3]
    search_data = [data["search"] for data in sample_data]
    selection = search_data[0]

    provider = Provider()
    provider.search = lambda query, translate: search_data
    mocked_select.return_value = selection

    track.track(provider, mock_args(title=title))

    mocked_select.assert_called_once_with('Select one of the following:\n   * = already tracked', search_data)
    mocked_confirm.assert_not_called()
    mocked_add.assert_not_called()