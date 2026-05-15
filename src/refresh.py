import argparse as ap
import asyncio
from typing import Protocol

from common.model import Series, SeriesConfig
from common.provider import Series
from common import cache
from common import utils

# This class is used for Duck-Typing; if it walks like a duck and quacks like a duck, it's a duck
class Provider(Protocol):
    def get_all(self, config: SeriesConfig) -> Series:
        ...


def add_args(parser: ap.ArgumentParser):
    parser.add_argument("--force", default=False, action="store_true", help="Force refresh all series")


@utils.as_async
def fetch_series(provider: Provider, config: SeriesConfig) -> Series:
    return provider.get_all(config)


async def _refresh(provider: Provider, args: ap.Namespace):
    cache.fix_configs()
    if args.force:
        where=True
    else:
        where = Series.keep_updated == True
    all_series = cache.result_of(cache.select_series(), where=where)

    configs = [series.config for series in all_series]
    updated: list[Series] = await asyncio.gather(*[fetch_series(provider, config) for config in configs])

    cache.update(updated)


def refresh(provider: Provider, args: ap.Namespace):
    _sync_refresh = utils.compose(asyncio.run, _refresh)
    _spinner_refresh = utils.with_spinner(_sync_refresh, "Refreshing")
    return _spinner_refresh(provider, args)
