import argparse as ap
import logging as log

from common import cache
from common import utils


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", nargs='+', help="The name(s) of shows to remove")
    parser.add_argument("-y", "--year", default=None, help="The year the series first aired.")
    parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")


def remove(args: ap.Namespace) -> None:
    to_remove = []
    for title in args.title:
        matches = cache.find(title, strict=args.strict)
        if len(matches) == 0:
            log.info(f"Series '{title}' was not tracked, so was not removed.")
        elif len(matches) == 1:
            to_remove.append(matches[0])
        else:
            log.warning(f"'{title}' is ambiguous ({len(matches)} matches). Retry with the -y/--year flag.")

    if to_remove == []:
        return

    log.info("The following series will be no longer be tracked:")
    for item in to_remove:
        log.info(f"  {item.stub_info()}")

    if not utils.confirm("Do you want to continue?"):
        return

    cache.delete(item.tvdb_id for item in to_remove)