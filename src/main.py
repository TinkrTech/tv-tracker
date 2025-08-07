import os
import dotenv
from dataclasses import dataclass
from typing import Optional
import utils
from pathlib import Path
import provider

API_URL = "https://api4.thetvdb.com/v4/"
CONFIG_PATH = "data/config.json"

@dataclass(slots=True, frozen=True)
class SeriesQuery:
    title: str
    language: Optional[str] = 'eng'
    year: Optional[str] = None


def add_to_config(config_path: Path, series: provider.Series) -> None:
    with config_path.open() as config_file:
        ...


def track(args: SeriesQuery):
    token = provider.tvdb_auth(os.getenv("TVDB_KEY"))
    results = provider.search(token, query={
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
        to_add = matches[0] if utils.confirm(f"Add the following? {matches[0]}\n(Y/n)") else None
    else:
        to_add = utils.select(f"Select one of the following:", matches)

    add_to_config(to_add)


def main():
    # tvdb = tvdb_v4_official.TVDB(os.getenv("TVDB_KEY"))
    args = SeriesQuery(title="Invincible", year="2021", language='eng')
    token = provider.tvdb_auth(os.getenv("TVDB_KEY"))
    results = provider.search(token, query={
        'query': args.title,
        'year': args.year,
        'type': 'series',
    })
    same_language = lambda item: item.language == args.language
    similar_name = lambda item: args.title in item.title
    equal = utils.intersect(similar_name, same_language)

    results = list(filter(equal, results))
    print(len(results))
    for result in results:
        print(result)


if __name__ == '__main__':
    ...
    dotenv.load_dotenv()
    main()