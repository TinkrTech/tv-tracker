"""
Note: This uses unsanitized inputs for routing. Use caution when loading config.toml
"""
import requests
import urllib.parse
import textwrap
from dataclasses import dataclass
from datetime import date

from common import model
from common import cache
from typing import Optional


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
    def __init__(self, api_token: str):
        self._session_token = self._get_session_token(api_token)

    def _get_session_token(self, api_token: str) -> str:
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

    def get_episodes(self, season_id: int) -> list[model.Episode]:
        raw = self._make_request(endpoint=f"seasons/{season_id}/extended")["data"]
        result = []
        for episode in raw["episodes"]:
            if episode["aired"] is not None:
                aired = date.fromisoformat(episode["aired"])
            else:
                aired = None

            result.append(model.Episode(
                tvdb_id=int(episode["id"]),
                title=episode["name"],
                number=episode["number"],
                aired=aired
            ))
        return result

    def get_series_info(self, series_id: int, use_language: Optional[str] = None, use_order: Optional[str] = None) -> model.Series:
        raw = self._make_request(endpoint=f"series/{series_id}/extended")["data"]

        keep_updated = raw\
            .get('status', {})\
            .get("keepUpdated", True)

        orders = [order["name"] for order in raw["seasonTypes"]]
        if use_order is None:
            use_order = orders[0]

        seasons = []
        for raw_season in raw.get("seasons"):
            season_id = int(raw_season["id"])
            episodes = self.get_episodes(season_id)
            season = model.Season(
                tvdb_id=season_id,
                number=int(raw_season['number']),
                order=raw_season["type"]["name"],
                episodes=episodes
            )
            seasons.append(season)

        title = raw["name"]
        if use_language is not None:
            translation = self._make_request(endpoint=f"series/{series_id}/translations/{use_language}")["data"]
            title = translation["name"]

        return model.Series(
            tvdb_id=int(series_id),
            title = title,
            year = raw["year"],
            last_aired = date.fromisoformat(raw["lastAired"]),
            retrieved = date.today(),
            keep_updated=keep_updated,
            orders=orders,
            use_order=use_order,
            seasons=seasons,
            use_language=use_language,
        )