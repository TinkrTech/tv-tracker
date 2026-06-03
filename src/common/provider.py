# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>

"""
Note: This uses unsanitized inputs for routing. Use caution when loading config.toml
"""
import requests
import urllib.parse
import textwrap
from dataclasses import dataclass
from datetime import date

from common.model import *
from common import cache
from typing import Optional, Iterable


@dataclass(slots=True, frozen=True)
class SearchResult:
    tvdb_id: int
    title: str
    original_title: str
    year: str | None
    language: str
    synopsis: str | None
    is_tracked: bool

    def __str__(self) -> str:
        indent = '  '
        if self.synopsis is None:
            fmt_synopsis = "[No synopsis]"
        else:
            fmt_synopsis = "\n".join(textwrap.wrap(self.synopsis, width=80, initial_indent=indent, subsequent_indent=indent))

        result = textwrap.dedent(f"""\
            tracked? {self.is_tracked}
            id: {self.tvdb_id}
            original_title: {self.original_title}
            title: {self.title}
            year: {self.year}
            language: {self.language}
        """).strip()
        result += f"\nsynopsis:\n{fmt_synopsis}"
        return result

    def stub_info(self) -> str:
        year = 'Unknown' if self.year is None else self.year
        tracked = "* " if self.is_tracked else "  "
        return f"{tracked}{self.title} ({year})"

    def full_info(self) -> str:
        return str(self)


class TVDBProvider:
    def __init__(self, session_token: str):
        self._session_token = session_token

    @staticmethod
    def fetch_session_token(api_token: str) -> str:
        """
        throws: requests.exceptions.HTTPError
        """
        data = r'{"apikey": "%s"}' % api_token
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(f"https://api4.thetvdb.com/v4/login", data=data, headers=headers)
        response.raise_for_status()
        token = response.json()["data"]["token"]
        return token

    def _make_request(self, endpoint: str, *, query: Optional[dict] = None) -> dict:
        if query is not None:
            encoded_query = urllib.parse.urlencode(query=query)
            endpoint += f"?{encoded_query}"
        AUTH_HEADER = {"Authorization": f"Bearer {self._session_token}"}
        response = requests.get(f"https://api4.thetvdb.com/v4/{endpoint}", headers=AUTH_HEADER)
        response.raise_for_status()
        return response.json()

    def search(self, query: dict, translate: str='eng') -> list[SearchResult]:
        filtered_query = {key: value for key, value in query.items() if value is not None}
        raw = self._make_request('search', query=filtered_query)
        results = []
        for result in raw['data']:
            series_id = int(result['tvdb_id'])

            default_name = result["name"]
            name = result\
                .get("translations", {})\
                .get(translate, default_name)

            default_synopsis = result.get('overview')
            synopsis = result\
                .get("overviews", {})\
                .get(translate, default_synopsis)

            results.append(SearchResult(
                tvdb_id=series_id,
                title=name,
                original_title=result["name"],
                language=result['primary_language'],
                year=result.get('year'),
                synopsis=synopsis,
                is_tracked=cache.has(series_id)
            ))
        return results

    def _fetch_all_episodes(self, series: Series, orders: Iterable[str]) -> list[Episode]:
        """
        Fetch all episodes and ordering for a series
        Updates the seasons in a series with SeasonEpisodes which are linked to episodes
        """
        # This would be a lot easier if the API returned what it said it does
        # Sorry in advance
        seasons = {
            (season.order, season.number): season
            for season in series.seasons
        }

        episodes: dict[int, Episode] = {}
        for order in orders:
            endpoint = f"series/{series.tvdb_id}/episodes/{order}/{series.config.language}"
            response = self._make_request(endpoint=endpoint)["data"]

            for raw_episode in response["episodes"]:
                episode_id = int(raw_episode["id"])
                episode = episodes.get(episode_id)
                if episode is None:
                    if raw_episode["aired"] is not None:
                        aired = date.fromisoformat(raw_episode["aired"])
                    else:
                        aired = None

                    episode = Episode(
                        tvdb_id=episode_id,
                        title=raw_episode["name"],
                        overview=raw_episode.get("overview", None),
                        aired=aired,
                    )
                    episodes[episode_id] = episode

                season_num = int(raw_episode["seasonNumber"])
                episode_num = int(raw_episode["number"])
                season = seasons[(order, season_num)] # if this fails, we have a problem
                season.season_episodes.append(SeasonEpisode(
                    season_id=season.tvdb_id,
                    episode_id=episode.tvdb_id,
                    season=season,
                    episode=episode,
                    number=episode_num,
                ))
        return list(episodes.values())


    def _extract_series(self, response: dict) -> Series:
        """Extract relevant info from the series/{series_id}/extended response"""
        raw = response
        keep_updated = raw\
            .get('status', {})\
            .get("keepUpdated", True)

        return Series(
            tvdb_id=int(raw["id"]),
            title = raw["name"],
            year = raw["year"],
            last_aired = date.fromisoformat(raw["lastAired"]),
            retrieved = date.today(),
            keep_updated=keep_updated,
        )

    def _extract_seasons(self, response: dict) -> list[Season]:
        """Extract seasons from the series/{series_id}/extended response"""
        seasons = []
        for raw in response.get("seasons", []):
            seasons.append(Season(
                tvdb_id=int(raw["id"]),
                number=int(raw["number"]),
                order=raw["type"]["type"],
                series_id=raw["seriesId"],
            ))
        return seasons

    def fetch_series(
        self,
        config: SeriesConfig,
    ) -> Series:
        raw = self._make_request(endpoint=f"series/{config.series_id}/extended")["data"]

        series = self._extract_series(raw)
        valid_orders = {order["id"]: order["type"] for order in raw["seasonTypes"]}

        if config.order not in valid_orders.values():
            config.order = valid_orders[raw["defaultSeasonType"]]

        if config.language is not None:
            translation = self._make_request(endpoint=f"series/{config.series_id}/translations/{config.language}")["data"]
            series.title = translation["name"]

        series.config = config

        seasons = self._extract_seasons(raw)
        series.seasons = seasons

        # Linked in function
        self._fetch_all_episodes(series, valid_orders.values())

        return series