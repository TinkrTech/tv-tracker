import os, sys
import dotenv

import argparse
from dataclasses import dataclass
from typing import Optional

import track
import refresh
import remove

from common import cache
from common import provider
from common import utils


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

    list_parser = commands.add_parser("list", parents=[defaults], help="Lists all tracked series.")
    list_parser.add_argument("-f", "--full", default=False, action="store_true", help="List the full details for each series.")

    refresh.get_parser(commands, defaults)
    remove.get_parser(commands, defaults)
    track.get_parser(commands, defaults)

    args = parser.parse_args()
    if args.no_animations:
        utils.USE_ANIMATIONS = False
    return args


def _list(args: argparse.Namespace) -> None:
    import textwrap

    tracked = common.cache.load()
    for i, series in enumerate(tracked, 1):
        print(f"{i} - {series.stub_info()}")
        if args.full:
            fmt_info = textwrap.indent(series.full_info(), '  ')
            print(fmt_info)
            print()


def main():
    args = get_args()

    fetch_token = utils.with_spinner(provider.tvdb_auth, "Fetching session token")
    token = fetch_token(os.getenv('TVDB_KEY'))

    cache.PATH = args.cache_path

    match args.command:
        case "track":
            track.track(token, args)
        case "list":
            _list(args)
        case "refresh":
            refresh.refresh(token, args)
        case "remove":
            remove.remove(args)


if __name__ == '__main__':
    dotenv.load_dotenv()
    try:
        main()
    except KeyboardInterrupt:
        print()