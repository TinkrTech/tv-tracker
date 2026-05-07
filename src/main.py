import os, dotenv, sys
import logging
import argparse
from pathlib import Path

import info
import fetch_episodes
import modify
import refresh
import remove
import track

from common.provider import TVDBProvider
from common import cache
from common import utils
from common import model


def get_args() -> argparse.Namespace:
    defaults = argparse.ArgumentParser(add_help=False)
    defaults.add_argument(
        "-c", "--cache-path",
        default=Path("data/cache.db"),
        type=Path,
        help="The location of the cache database"
    )

    defaults.add_argument(
        "-A", "--no-animations",
        default=False,
        action="store_true",
        help="Disable loading animations"
    )
    defaults.add_argument(
        "-q", "--quiet",
        default=False,
        action="store_true",
        help="Run non-interactively. Disables non-functional output and auto-confirm all input"
    )

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
    list_parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")

    info.add_args(make_parser(          "info",             "List info for all matched series."))
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
    if len(args.title) > 0:
        tracked = cache.find(args.title, strict=args.strict)
    else:
        tracked = cache.list_all()

    for i, series in enumerate(tracked, 1):
        print(f"{i} - {series.stub_info()}")


def init_error_logger() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    warning_handler = logging.StreamHandler(sys.stderr)
    warning_handler.setLevel(logging.WARNING)
    warning_formatter = logging.Formatter("{levelname}: {message}", style="{")
    warning_handler.setFormatter(warning_formatter)
    logger.addHandler(warning_handler)


def init_verbose_logger() -> None:
    logger = logging.getLogger()
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_fmt = logging.Formatter("{message}", style="{")
    info_handler.setFormatter(info_fmt)
    info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    logger.addHandler(info_handler)


def initialize_cache(args: argparse.Namespace):
    args.cache_path: Path = args.cache_path
    old_cache = None
    old_default_cache = Path("data/cache.toml")

    if args.cache_path.suffix == 'toml':
        old_cache = args.cache_path
        args.cache_path = args.cache_path.with_suffix('db')
    elif not args.cache_path.exists() and old_default_cache.exists():
        old_cache = old_default_cache

    cache.initialize(args.cache_path)

    if old_cache is not None and old_cache.exists():
        logging.info(f"The cache '{old_cache}' will be upgraded to sqlite.")
        logging.info(f"New data will be saved to '{args.cache_path}'")
        try:
            cache.migrate_toml(old_cache)
        except Exception as e:
            args.cache_path.unlink()
            raise e
    elif old_cache is not None:
        logging.info(f"Cache file '{old_cache}' was not found. A new cache will be started.")
    else:
        logging.debug(f"No existing cache.")

def main():
    init_error_logger()
    args = get_args()
    dotenv.load_dotenv()
    if not args.quiet:
        init_verbose_logger()

    initialize_cache(args)

    utils.USE_ANIMATIONS = not args.no_animations
    utils.QUIET = args.quiet

    make_provider = utils.with_spinner(TVDBProvider, "Fetching session token")

    match args.command:
        case "info":
            info.info(args)
        case "list":
            _list(args)
        case "remove":
            remove.remove(args)
        case "modify":
            modify.modify(args)
        case "track":
            track.track(
                make_provider(os.getenv('TVDB_KEY')),
                args
            )
        case "refresh":
            refresh.refresh(
                make_provider(os.getenv('TVDB_KEY')),
                args
            )
        case "fetch-episodes":
            fetch_episodes.fetch_episodes(
                make_provider(os.getenv('TVDB_KEY')),
                args
            )



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()