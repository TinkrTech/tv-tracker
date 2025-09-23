import argparse as ap
import textwrap
import logging as log
from typing import Protocol

from common.provider import SearchResult
from common import utils
from common import cache
from common.model import Series

# This class is used for Duck-Typing; if it walks like a duck and quacks like a duck, it's a duck
class Provider(Protocol):
    def search(self, query: dict|None, translate: str) -> list[SearchResult]:
        ...

    def get_series_info(self, series_id: int, use_language: str|None, use_order: str|None) -> Series:
        ...


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", help="The title of the show to add")
    parser.add_argument("-l", "--language", help="The three letter original language of the series.")
    parser.add_argument("-t", "--translate", default="eng", help="The three letter translation lanuage for the title and synopsis.")
    parser.add_argument("-y", "--year", default=None, help="The year the series first aired.")


def track(provider: Provider, args: ap.Namespace):
    year = args.year if args.year is not None else 'Any'
    query_stub = f"title={args.title} year={year} language={args.language}"

    query = {
        'query': args.title,
        'year': args.year,
        'type': 'series',
    }
    if args.language is not None:
        query["language"] = args.language

    _search = utils.with_spinner(provider.search, message=f"Querying TVDB for {query_stub}")
    results = _search(query=query, translate=args.translate)

    same_language = lambda x: args.language is None or args.language == x.language
    title_is_similar = lambda x: args.title in x.title
    matches = list(filter(utils.intersect(same_language, title_is_similar), results))

    if len(matches) == 0:
        log.info(f"No results")
        return
    elif len(matches) == 1:
        fmt_result = textwrap.indent(str(matches[0]), '  ')
        if not utils.confirm(f"Found the following:\n{fmt_result}\nStart tracking?", default='y'):
            return
        to_add = matches[0]
    else:
        to_add = utils.select(f"Select one of the following:\n   * = already tracked", matches)

    _get_series_info = utils.with_spinner(provider.get_series_info, "Fetching full series info")
    to_track = _get_series_info(series_id=to_add.tvdb_id, use_language=args.translate)
    cache.add(to_track)
