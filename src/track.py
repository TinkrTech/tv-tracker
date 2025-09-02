import argparse as ap
import textwrap

from common import utils
from common import provider
from common import series


def get_parser(parent: ap._SubParsersAction) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = parent.add_parser('track', help="Adds a new series to the configuration to be tracked.")
    # see main.py for inherrited args
    parser.add_argument("title", help="The title of the show to add")
    parser.add_argument("-L", "--language", default="eng", help="The three letter acronym for the language of the series.")
    parser.add_argument("-y", "--year", default=None, help="The year the series first aired.")
    parser.set_defaults(which='track')
    return parser


def track(session_token: str, args: ap.Namespace):
    results = provider.search(session_token, query={
        'query': args.title,
        'year': args.year,
        'type': 'series',
    })
    same_language = lambda item: item.language == args.language
    similar_name = lambda item: args.title in item.title
    equal = utils.intersect(similar_name, same_language)

    matches = list(filter(equal, results))
    if len(matches) == 0:
        year = args.year if args.year is not None else 'Any'
        stub = f"title={args.title} year={year} language={args.language}"
        print(f"No results for {stub}...")
        return
    elif len(matches) == 1:
        fmt_result = textwrap.indent(str(matches[0]), '  ')
        if not utils.confirm(f"Found the following:\n{fmt_result}\nStart tracking?", default='y'):
            return
        to_add = matches[0]
    else:
        to_add = utils.select(f"Select one of the following:", matches)

    to_track = provider.get_series_info(session_token, to_add.tvdb_id)
    series.add_to_config(args.config_path, to_track)
