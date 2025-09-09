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


@dataclass(slots=True, frozen=True)
class SearchResult:
    tvdb_id: int
    title: str
    year: str | None
    language: str
    synopsis: str | None
    is_tracked: bool

    def __str__(self) -> str:
        indent = '  '
        fmt_synopsis = "\n".join(textwrap.wrap(self.synopsis, width=80, initial_indent=indent, subsequent_indent=indent))
        result = textwrap.dedent(f"""\
            tracked? {self.is_tracked}
            id: {self.tvdb_id}
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


def tvdb_auth(api_token: str) -> str:
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


def _make_request(session_token: str, endpoint: str, *, query: dict = None) -> dict:
    if query is not None:
        query = urllib.parse.urlencode(query=query)
        endpoint += f"?{query}"
    AUTH_HEADER = {"Authorization": f"Bearer {session_token}"}
    response = requests.get(f"https://api4.thetvdb.com/v4/{endpoint}", headers=AUTH_HEADER)
    response.raise_for_status()
    return response.json()


def search(session_token: str, query: dict) -> list[SearchResult]:
    filtered_query = {key: value for key, value in query.items() if value is not None}
    raw = _make_request(session_token, 'search', query=filtered_query)
    results = []
    for result in raw['data']:
        series_id = int(result['tvdb_id'])
        results.append(SearchResult(
            tvdb_id=series_id,
            title=result['name'],
            language=result['primary_language'],
            year=result.get('year'),
            synopsis=result.get('overview'),
            is_tracked=cache.has(series_id)
        ))
    return results


def get_episodes(session_token: str, season_id: int) -> list[model.Episode]:
    raw = _make_request(session_token, endpoint=f"seasons/{season_id}/extended")["data"]
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


def get_series_info(session_token: str, series_id: int, use_order: str = None) -> model.Series:
    raw = _make_request(session_token, endpoint=f"series/{series_id}/extended")["data"]

    keep_updated = raw\
        .get('status', {})\
        .get("keepUpdated", True)

    orders = [order["name"] for order in raw["seasonTypes"]]
    if use_order is None:
        use_order = orders[0]

    seasons = []
    for raw_season in raw.get("seasons"):
        season_id = int(raw_season["id"])
        episodes = get_episodes(session_token, season_id)
        season = model.Season(
            tvdb_id=season_id,
            number=int(raw_season['number']),
            order=raw_season["type"]["name"],
            episodes=episodes
        )
        seasons.append(season)

    return model.Series(
        tvdb_id=int(series_id),
        title = raw["name"],
        year = raw["year"],
        last_aired = date.fromisoformat(raw["lastAired"]),
        retrieved = date.today(),
        keep_updated=keep_updated,
        use_order=use_order,
        orders=orders,
        seasons=seasons,
    )