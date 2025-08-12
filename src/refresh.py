import argparse as ap

def get_parser(parent: ap._SubParsersAction) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = parent.add_parser('refresh', help="Pulls the latest information for tracked series.")
    # see main.py for inherrited args
    parser.add_argument("--force", default=False, action="store_true", help="Force refresh all series")
    parser.set_defaults(which='refresh')
    return parser