"""
Note: This uses unsanitized inputs for routing. Use caution when loading config.toml
"""
import requests
import urllib.parse
from dataclasses import dataclass
from typing import Optional
import textwrap


@dataclass(slots=True, frozen=True)
class Series:
    tvdb_id: str
    title: str
    language: str
    release_year: str
    synopsis: str
    status: str
    thumbnail: Optional[str]

    def __str__(self):
        return textwrap.dedent(f"""
            id: {self.tvdb_id}
            title: {self.title}
            year: {self.release_year}
            synopsis: {self.synopsis}
        """.strip('\n'))

    @classmethod
    def from_dict(cls, data: dict):
        thumbnail = data.get('thumbnail', data.get('image_url', None))
        return Series(
            tvdb_id=data['tvdb_id'],
            title=data['name'],
            language=data['primary_language'],
            release_year=data['year'],
            synopsis=data['overview'],
            thumbnail=thumbnail,
            status=data['status'],
        )

API_URL = "https://api4.thetvdb.com/v4"

def tvdb_auth(api_token: str) -> str:
    """
    throws: requests.exceptions.HTTPError
    """
    data = r'{"apikey": "%s"}' % api_token
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{API_URL}/login", data=data, headers=headers)
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

def search(session_token: str, query: dict) -> list[Series]:
    filtered_query = {key: value for key, value in query.items() if value is not None}
    raw = _make_request(session_token, 'search', query=filtered_query)
    return [Series.from_dict(result) for result in raw['data']]

def series_info(session_token: str, tvdb_id: str):
    raw = _make_request(session_token, endpoint=f"series/{tvdb_id}/extended")
    return raw["data"]
