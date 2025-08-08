import os
import dotenv
import tomllib
import textwrap
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import utils
import provider


API_URL = "https://api4.thetvdb.com/v4/"
CONFIG_PATH = Path("data/config.json")

@dataclass(slots=True, frozen=True)
class SeriesQuery:
    title: str
    language: Optional[str] = 'eng'
    year: Optional[str] = None


def track(session_token: str, args: SeriesQuery):
    results = provider.search(session_token, query={
        'query': args.title,
        'year': args.year,
        'type': 'series',
    })
    same_language = lambda item: item.language == args.language
    similar_name = lambda item: args.title in item.title
    equal = utils.intersect(similar_name, same_language)

    matches = list(filter(equal, results))
    if len(matches) == 0:
        print(f"No results for {args}..")
        return
    elif len(matches) == 1:
        to_add = matches[0] if utils.confirm(f"Found:\n{matches[0]}\nStart tracking?(Y/n)") else None
    else:
        to_add = utils.select(f"Select one of the following:", matches)

    series = provider.get_series_info(session_token, to_add.tvdb_id)

    with config_path.open('a') as cfg:
        cfg.write(str(series))


def main():
    token = provider.tvdb_auth(os.getenv("TVDB_KEY"))


if __name__ == '__main__':
    dotenv.load_dotenv()
    main()