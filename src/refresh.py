import argparse as ap
import asyncio
from typing import Protocol

from common.model import Series
from common import cache
from common import utils


# This class is used for Duck-Typing; if it walks like a duck and quacks like a duck, it's a duck
class Provider(Protocol):
    def get_series_info(self, series_id: int, use_language: str|None, use_order: str|None) -> Series:
        ...


def add_args(parser: ap.ArgumentParser):
    parser.add_argument("--force", default=False, action="store_true", help="Force refresh all series")


@utils.as_async
def fetch_series(provider: Provider, tracked: Series, force: bool = False) -> Series:
    if not tracked.keep_updated and not force:
        return tracked

    fetched = provider.get_series_info(
        tracked.tvdb_id,
        use_language=tracked.use_language,
        use_order=tracked.use_order
    )

    return fetched


async def _refresh(provider: Provider, args: ap.Namespace):
    bound_fetch = lambda tracked: fetch_series(provider, tracked, args.force)

    all_series = cache.list_all()
    updated: list[Series] = await asyncio.gather(*[bound_fetch(series) for series in all_series])
    cache.update(updated)


def refresh(provider: Provider, args: ap.Namespace):
    _sync_refresh = utils.compose(asyncio.run, _refresh)
    _spinner_refresh = utils.with_spinner(_sync_refresh, "Refreshing")
    return _spinner_refresh(provider, args)