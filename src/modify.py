import argparse as ap
import logging as log

from sqlalchemy.orm import selectinload

from common import cache
from common.model import Series

def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", help="The series to update.")
    parser.add_argument("-o", "--order", help="Change which season order should be used when fetching updates.")
    parser.add_argument("-l", "--language")
    parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")


def modify(args: ap.Namespace):
    all_series = cache.find(
        args.title,
        strict=args.strict,
        query_options=[selectinload(Series.config)]
    )

    updated_series = []
    for series in all_series:
        orders = cache.series_orders(series.tvdb_id)
        series.config.language = args.language

        if args.order not in orders:
            log.warning(f"Supported orders for \"{series.stub_info()}\" are {orders}. Skipping...")
        else:
            series.config.order = args.order

        updated_series.append(series)

    cache.update(updated_series)