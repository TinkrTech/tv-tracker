import argparse as ap

import common.cache

def get_parser(subparser: ap._SubParsersAction, defaults: ap.ArgumentParser) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = subparser.add_parser('modify', parents=[defaults], help="Modify series' configuration(s).")
    # see main.py for inherrited args
    parser.add_argument("series", nargs="+", help="The series to update.")
    parser.add_argument("-o", "--use-order", help="Change which season order should be used when fetching updates.")

    parser.set_defaults(which='modify')
    return parser


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