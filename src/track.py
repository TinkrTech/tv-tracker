import argparse as ap
import textwrap

from common import utils
from common import provider
from common import cache

def get_parser(subparser: ap._SubParsersAction, defaults: ap.ArgumentParser) -> ap.ArgumentParser:
    parser: ap.ArgumentParser = subparser.add_parser('track', parents=[defaults], help="Adds a new series to the configuration to be tracked.")
    # see main.py for inherrited args
    parser.set_defaults(which='track')
    parser.add_argument("title", help="The title of the show to add")
    parser.add_argument("-l", "--language", default="eng", help="The three letter original language of the series.")
    parser.add_argument("-t", "--translate", default="eng", help="The three letter translation lanuage for the title and synopsis.")
    parser.add_argument("-y", "--year", default=None, help="The year the series first aired.")
    return parser


def track(session_token: str, args: ap.Namespace):
    year = args.year if args.year is not None else 'Any'
    query_stub = f"title={args.title} year={year} language={args.language}"

    _search = utils.with_spinner(provider.search, message=f"Querying TVDB for {query_stub}")
    results = _search(session_token, query={
        'query': args.title,
        'year': args.year,
        'language': args.language,
        'type': 'series',
    }, translate=args.translate)

    matches = [result for result in results
        if result.language == args.language
        and args.title in result.title
    ]
    if len(matches) == 0:
        print(f"No results")
        return
    elif len(matches) == 1:
        fmt_result = textwrap.indent(str(matches[0]), '  ')
        if not utils.confirm(f"Found the following:\n{fmt_result}\nStart tracking?", default='y'):
            return
        to_add = matches[0]
    else:
        to_add = utils.select(f"Select one of the following:\n   * = already tracked", matches)

    _get_series_info = utils.with_spinner(provider.get_series_info, "Fetch full series info")
    to_track = _get_series_info(session_token, to_add.tvdb_id, use_language=args.translate)
    cache.add(to_track)
