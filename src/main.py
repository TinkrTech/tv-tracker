import os, dotenv, sys
import logging
import argparse

import track
import refresh
import remove
import modify
import fetch_episodes

from common.provider import TVDBProvider
from common import cache
from common import utils
from common import model


def get_args() -> argparse.Namespace:
    defaults = argparse.ArgumentParser(add_help=False)
    defaults.add_argument(
        "-c", "--cache-path",
        default="data/cache.toml",
        help="The location of config.toml"
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
    list_parser.add_argument("-f", "--full", default=False, action="store_true", help="List the full details for each series.")
    list_parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")

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

    tracked = cache.load()

    if len(args.title) > 0:
        if args.strict:
            tracked = list(cache.strict_find(args.title))
        else:
            tracked = list(cache.fuzzy_find(args.title))


    for i, series in enumerate(tracked, 1):
        print(f"{i} - {series.stub_info()}")
        if args.full:
            fmt_info = textwrap.indent(series.full_info(), '  ')
            print(fmt_info)
            print()



def init_logger(is_quiet: bool = False):
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    if not is_quiet:
        info_handler = logging.StreamHandler(sys.stdout)
        info_handler.setLevel(logging.INFO)
        info_fmt = logging.Formatter("{message}", style="{")
        info_handler.setFormatter(info_fmt)
        info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
        logger.addHandler(info_handler)

    warning_handler = logging.StreamHandler(sys.stderr)
    warning_handler.setLevel(logging.WARNING)
    warning_formatter = logging.Formatter("{levelname}: {message}", style="{")
    warning_handler.setFormatter(warning_formatter)
    logger.addHandler(warning_handler)

    return logger


def main():
    args = get_args()
    dotenv.load_dotenv()
    init_logger(is_quiet=args.quiet)

    cache.PATH = args.cache_path
    utils.USE_ANIMATIONS = not args.no_animations
    utils.QUIET = args.quiet

    make_provider = utils.with_spinner(TVDBProvider, "Fetching session token")

    match args.command:
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