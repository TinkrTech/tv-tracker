import os, sys
import dotenv

import argparse
from dataclasses import dataclass
from typing import Optional

import track
import refresh
import remove
import modify
import fetch_episodes

from common import cache
from common import provider
from common import utils
from common import model


def get_args() -> argparse.Namespace:
    defaults = argparse.ArgumentParser(add_help=False)
    defaults.add_argument("-c", "--cache-path", default="data/cache.toml", help="The location of config.toml")
    defaults.add_argument("-A", "--no-animations", default=False, help="Disable loading animations", action="store_true")

    parser = argparse.ArgumentParser(sys.argv[0], parents=[defaults], description="Keep track of the shows you watch, all in one place.")
    commands = parser.add_subparsers(
        dest="command",
        title="Subcommands",
        required=True
    )

    def make_parser(name: str, description: str) -> argparse.ArgumentParser:
        nonlocal commands, defaults
        result: argparse.ArgumentParser = commands.add_parser(name, parents=[defaults], help=description)
        result.set_defaults(which=name)
        return result

    list_parser = make_parser(          "list",             "Lists all tracked series.")
    list_parser.add_argument("title", nargs="*", help="Only list the info for series containing this title.")
    list_parser.add_argument("-f", "--full", default=False, action="store_true", help="List the full details for each series.")

    refresh.add_args(make_parser(       "refresh",          "Pulls the latest information for tracked series."))
    remove.add_args(make_parser(        "remove",           "Stop tracking one or more series."))
    track.add_args(make_parser(         "track",            "Adds a new series to the configuration to be tracked."))
    modify.add_args(make_parser(        "modify",           "Modify series' configuration(s)."))
    fetch_episodes.add_args(make_parser("fetch-episodes",   "Fetches episodes list for a tracked series and displays it."))

    args = parser.parse_args()
    if args.no_animations:
        utils.USE_ANIMATIONS = False
    return args


def _list(args: argparse.Namespace) -> None:
    import textwrap
    from itertools import chain

    tracked = cache.load()

    if len(args.title) > 0:
        tracked = cache.fuzzy_find(args.title)

    for i, series in enumerate(tracked, 1):
        print(f"{i} - {series.stub_info()}")
        if args.full:
            fmt_info = textwrap.indent(series.full_info(), '  ')
            print(fmt_info)
            print()


def main():
    args = get_args()

    fetch_token = utils.with_spinner(provider.tvdb_auth, "Fetching session token")


    cache.PATH = args.cache_path
    utils.USE_ANIMATIONS = not args.no_animations

    match args.command:
        case "list":
            _list(args)
        case "remove":
            remove.remove(args)
        case "modify":
            modify.modify(args)
        case "track":
            token = fetch_token(os.getenv('TVDB_KEY'))
            track.track(token, args)
        case "refresh":
            token = fetch_token(os.getenv('TVDB_KEY'))
            refresh.refresh(token, args)
        case "fetch-episodes":
            token = fetch_token(os.getenv('TVDB_KEY'))
            fetch_episodes.fetch_episodes(token, args)



if __name__ == '__main__':
    dotenv.load_dotenv()
    try:
        main()
    except KeyboardInterrupt:
        print()