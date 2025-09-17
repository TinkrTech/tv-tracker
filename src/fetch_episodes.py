import argparse as ap

from common import utils
from common import cache
from common import provider
from common.model import Series, Episode


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", help="The title of the series.")
    parser.add_argument("-s", "--season", type=int, help="The season number to fetch.")


def fetch_episodes(session_token: str, args: ap.Namespace) -> None:
    tracked = list(cache.fuzzy_find(args.title))
    if len(tracked) == 0:
        print(f"WARNING: No tracked series matched the title '{args.title}'. Skipping...")
        return
    if len(tracked) > 1:
        print(f"Matched {len(tracked)} items.")
        selection = utils.select("Select one of the following", tracked)
    else:
        selection = tracked[0]

    if args.season is not None and selection.get_season_count() < args.season:
        print(f"WARNING: {selection.title} has no season {args.season}. Skipping...")
        return

    _get_series_info = utils.with_spinner(provider.get_series_info, "Fetching full series info")
    series_info: Series = _get_series_info(session_token, selection.tvdb_id, use_order=selection.use_order, use_language=selection.use_language)

    # filter seasons
    seasons = [
        season for season in series_info.seasons
        if season.order == selection.use_order
            and season.number != 0
    ]
    if args.season is not None:
        seasons = [season for season in seasons if season.number == args.season]

    if len(seasons) == 0:
        season_number = "seasons" if args.season is None else f"season {args.season}"
        print(f"WARNING: Fetching '{selection.title}' returned no {season_number} when using {selection.use_order}. Skipping...")
        return

    # Output
    for i, season in enumerate(seasons):
        for episode in season.episodes:
            print(f"{episode.aired}\tS{season.number:02d}E{episode.number:02d} - {episode.title}")
        if i != len(seasons) - 1:
            print()