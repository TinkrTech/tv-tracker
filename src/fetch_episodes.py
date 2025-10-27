import argparse as ap
from typing import Protocol
import logging as log


from common import utils
from common import cache
from common.model import Series, Episode


# This class is used for Duck-Typing; if it walks like a duck and quacks like a duck, it's a duck
class Provider(Protocol):
    def get_series_info(self, series_id: int, use_language: str|None, use_order: str|None) -> Series:
        ...


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", help="The title of the series.")
    parser.add_argument("-s", "--season", type=int, help="The season number to fetch.")
    parser.add_argument("--name-only", default=False, action="store_true", help="Only output the name of the series.")


def fetch_episodes(provider: Provider, args: ap.Namespace) -> None:
    tracked = list(cache.find(args.title))
    if len(tracked) == 0:
        log.warning(f"No tracked series matched the title '{args.title}'. Skipping...")
        return
    if len(tracked) > 1:
        log.info(f"Matched {len(tracked)} items.")
        selection: Series = utils.select("Select one of the following", tracked)
    else:
        selection = tracked[0]

    if args.season is not None and selection.get_season_count() < args.season:
        log.warning(f"{selection.title} has no season {args.season}. Skipping...")
        return

    _get_series_info = utils.with_spinner(provider.get_series_info, "Fetching full series info")
    series_info: Series = _get_series_info(selection.tvdb_id, use_order=selection.use_order, use_language=selection.use_language)

    # filter seasons
    seasons = [
        season for season in series_info.seasons
        if season.order == selection.use_order
            and season.number != 0
            and len(season.episodes) > 0
    ]
    if args.season is not None:
        seasons = [season for season in seasons if season.number == args.season]

    if len(seasons) == 0:
        season_number = "seasons" if args.season is None else f"season {args.season}"
        log.warning(f"Fetching '{selection.title}' returned no {season_number} when using {selection.use_order}. Skipping...")
        return

    # Output
    for i, season in enumerate(seasons):
        for episode in season.episodes:
            name = f"S{season.number:02d}E{episode.number:02d} - {episode.title}"
            if args.name_only:
                print(f"{name}")
            else:
                print(f"{episode.aired}\t{name}")
        if i != len(seasons) - 1:
            print()