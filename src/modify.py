import argparse as ap
import logging as log
import common.cache

def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", nargs="+", help="The series to update.")
    parser.add_argument("-o", "--use-order", help="Change which season order should be used when fetching updates.")


def modify(args: ap.Namespace):
    tracked_series = common.cache.fuzzy_find(args.title)

    updated_series = []
    for series in tracked_series:
        if args.use_order not in series.orders:
            log.warning(f"Supported orders for \"{series.stub_info()}\" are {series.orders}. Skipping...")
        else:
            series = series.using(
                use_order=args.use_order
            )

        updated_series.append(series)

    common.cache.update(updated_series)