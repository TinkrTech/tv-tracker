import argparse as ap
import logging as log

from common import cache
from common import utils


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", nargs='+', help="The name(s) of shows to remove")
    parser.add_argument("-y", "--year", default=None, help="The year the series first aired.")


def remove(args: ap.Namespace) -> None:
    all_series = cache.load()

    to_remove = []
    for title in args.title:
        matches = [series for series in all_series if series.title == title]
        if len(matches) == 0:
            log.info(f"Series '{title}' was not tracked, so was not removed.")
        elif len(matches) == 1:
            to_remove.append(matches[0])
        else:
            log.warning(f"'{title}' is ambiguous ({len(matches)} matches). Retry with the -y/--year flag.")

    log.info("The following series will be no longer be tracked:")
    for item in to_remove:
        log.info(f"  {item.stub_info()}")

    if not utils.confirm("Do you want to continue?"):
        return

    updated = [series for series in all_series if series not in to_remove]
    cache.update(updated)