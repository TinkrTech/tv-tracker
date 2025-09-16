import argparse as ap

import common.cache

def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("series", nargs="+", help="The series to update.")
    parser.add_argument("-o", "--use-order", help="Change which season order should be used when fetching updates.")


def modify(args: ap.Namespace):
    tracked_series = common.cache.load()
    updated_series = []
    for series in tracked_series:
        if series.title not in args.series:
            pass
        elif args.use_order not in series.orders:
            print(f"WARNING: Supported orders for \"{series.stub_info()}\" are {series.orders}. Skipping...")
        else:
            series = series.using(
                use_order=args.use_order
            )

        updated_series.append(series)

    common.cache.update(updated_series)