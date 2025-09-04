import argparse as ap

def get_parser(subparser: ap._SubParsersAction, defaults: ap.ArgumentParser) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = subparser.add_parser('refresh', parents=[defaults], help="Pulls the latest information for tracked series.")
    # see main.py for inherrited args
    parser.add_argument("--force", default=False, action="store_true", help="Force refresh all series")
    parser.set_defaults(which='refresh')
    return parser