import argparse as ap
from common import cache
from common import utils

def get_parser(subparser: ap._SubParsersAction, defaults: ap.ArgumentParser) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = subparser.add_parser('remove', parents=[defaults], help="Stop tracking one or more series.")
    # see main.py for inherrited args
    parser.add_argument("title", nargs='+', help="The name(s) of shows to remove")
    parser.add_argument("-y", "--year", default=None, help="The year the series first aired.")
    parser.set_defaults(which='remove')
    return parser

def remove(args: ap.Namespace) -> None:
    all_series = cache.load(args.cache_path)

    to_remove = []
    for title in args.title:
        matches = [series for series in all_series if series.title == title]
        if len(matches) == 0:
            print(f"Series '{title}' was not tracked, so was not removed.")
        elif len(matches) == 1:
            to_remove.append(matches[0])
        else:
            print(f"'{title}' is ambiguous ({len(matches)} matches). Retry with the -y/--year flag")

    print("The following series will be no longer be tracked:")
    for item in to_remove:
        print(f"  {item.stub_info()}")

    if not utils.confirm("Do you want to continue?"):
        return

    updated = [series for series in all_series if series not in to_remove]
    cache.update(args.cache_path, updated)