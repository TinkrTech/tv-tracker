import os
import dotenv

from dataclasses import dataclass
from typing import Optional

import utils
import provider
import series

@dataclass(slots=True, frozen=True)
class TrackArgs:
    title: str
    config_path: str
    language: Optional[str] = 'eng'
    year: Optional[str] = None


def track(session_token: str, args: TrackArgs):
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

    to_track = provider.get_series_info(session_token, to_add.tvdb_id)
    series.add_to_config(args.config_path, to_track)


def main():
    # token = provider.tvdb_auth(os.getenv("TVDB_KEY"))
    tracked = series.from_config("data/config.toml")
    for series in tracked:
        print(series)
        print()

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()