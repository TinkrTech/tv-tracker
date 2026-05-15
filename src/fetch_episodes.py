import argparse as ap
import logging as log

from common import utils
from common import cache
from common.model import Series, Season


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", help="The title of the series.")
    parser.add_argument("-s", "--season", type=int, help="The season number to fetch.")
    parser.add_argument("--name-only", default=False, action="store_true", help="Only output the name of the series.")


def fetch_episodes(args: ap.Namespace) -> None:
    tracked = cache.find(args.title)

    if len(tracked) == 0:
        log.warning(f"No tracked series matched the title '{args.title}'. Skipping...")
        return
    if len(tracked) > 1:
        log.info(f"Matched {len(tracked)} items.")
        selection: Series = utils.select("Select one of the following", tracked)
    else:
        selection = tracked[0]

    where = [
        Season.order == selection.config.order,
    ]

    if args.season is not None:
        where.append(Season.number == args.season)
    else:
        where.append(Season.number != 0)

    seasons = cache.result_of(
        cache.select_seasons(series_id=selection.tvdb_id),
        where=where,
        order_by=Season.number
    )

    if args.season is not None and len(seasons) == 0:
        log.warn(f"{selection.title} ({selection.config.order} order) has no season {args.season}...")

    for i, season in enumerate(seasons):
        # There is no guarantee that episodes are in order...
        season_episodes = sorted(
            season.season_episodes,
            key=lambda x: x.number
        )

        for season_episode in season_episodes:
            episode = season_episode.episode
            episode_num = season_episode.number
            name = f"S{season.number:02d}E{episode_num:02d} - {episode.title}"
            if args.name_only:
                print(f"{name}")
            else:
                print(f"{episode.aired}\t{name}")

        if i != len(seasons) - 1:
            print()