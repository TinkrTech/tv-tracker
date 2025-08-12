import os, sys
import dotenv

import argparse
from dataclasses import dataclass
from typing import Optional

import track
import refresh
from common import provider


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(sys.argv[0], description="Keep track of the shows you watch, all in one place.")
    parser.add_argument("-c", "--config-path", default="data/config.toml", help="The location of config.toml")

    subparsers = parser.add_subparsers(
        dest="command",
        title="Subcommands",
        required=True
    )
    track.get_parser(subparsers)
    refresh.get_parser(subparsers)

    return parser.parse_args()


def main():
    args = get_args()
    token = provider.tvdb_auth(os.getenv('TVDB_KEY'))
    match args.command:
        case "track":
            track.track(token, args)
        case "refresh":
            print("Refreshing!")

    # token = provider.tvdb_auth(os.getenv("TVDB_KEY"))
    # tracked = series.from_config("data/config.toml")
    # for series in tracked:
    #     print(series)
    #     print()

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()