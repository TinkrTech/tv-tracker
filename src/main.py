import os, sys
import dotenv

import argparse
from dataclasses import dataclass
from typing import Optional

import track
import refresh
from common import provider
from common import utils


def get_args() -> argparse.Namespace:
    defaults = argparse.ArgumentParser(add_help=False)
    defaults.add_argument("-c", "--config-path", default="data/config.toml", help="The location of config.toml")
    defaults.add_argument("-A", "--no-animations", default=False, help="Disable loading animations", action="store_true")

    parser = argparse.ArgumentParser(sys.argv[0], parents=[defaults], description="Keep track of the shows you watch, all in one place.")
    commands = parser.add_subparsers(
        dest="command",
        title="Subcommands",
        required=True
    )

    track.get_parser(commands, defaults)
    refresh.get_parser(commands, defaults)

    args = parser.parse_args()
    if args.no_animations:
        utils.USE_ANIMATIONS = False
    return args

def main():
    args = get_args()
    token = provider.tvdb_auth(os.getenv('TVDB_KEY'))
    match args.command:
        case "track":
            track.track(token, args)
        case "refresh":
            refresh.refresh(token, args)

    # token = provider.tvdb_auth(os.getenv("TVDB_KEY"))
    # tracked = series.from_config("data/config.toml")
    # for series in tracked:
    #     print(series)
    #     print()

if __name__ == '__main__':
    dotenv.load_dotenv()
    try:
        main()
    except KeyboardInterrupt:
        print()