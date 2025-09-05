import argparse as ap
import asyncio

from common.model import Series
from common import cache
from common import provider
from common import utils

def get_parser(subparser: ap._SubParsersAction, defaults: ap.ArgumentParser) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = subparser.add_parser('refresh', parents=[defaults], help="Pulls the latest information for tracked series.")
    # see main.py for inherrited args
    parser.add_argument("--force", default=False, action="store_true", help="Force refresh all series")
    parser.set_defaults(which='refresh')
    return parser


@utils.as_async
def fetch_series(session_token: str, cached: Series, force: bool = False) -> Series:
    if not cached.keep_updated and not force:
        return cached

    fetched = provider.get_series_info(session_token, cached.tvdb_id, use_order=cached.use_order)
    return fetched


async def _refresh(session_token: str, args: ap.Namespace):
    bound_fetch = lambda cached: fetch_series(session_token, cached, args.force)

    all_series = cache.load(args.cache_path)
    updated: list[Series] = await asyncio.gather(*[bound_fetch(series) for series in all_series])
    cache.update(args.cache_path, updated)


def refresh(session_token: str, args: ap.Namespace):
    return asyncio.run(_refresh(session_token, args))