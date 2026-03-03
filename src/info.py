# So named to avoid name shadowing for stdlib module
import argparse as ap
import logging as log
import dataclasses
from typing import Any

from common import cache
from common.model import Series


SERIES_FIELDS = tuple(field.name for field in dataclasses.fields(Series)
                      if field.name not in ["seasons"])


def validate_field_name(value: str):
    if value.lower() not in SERIES_FIELDS:
        msg = f"field must be one of {SERIES_FIELDS} not '{value}'\n"
        log.error(msg)
        raise ValueError(msg)
    return value.lower()


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", nargs='+', help="The name of the tracked show(s) to match.")

    parser.add_argument("-f", "--fields", nargs="*", type=validate_field_name, help="The fields to return. Returns all if not specified")

    parser.add_argument("--format", choices=("csv", "tsv", "toml"), default="tsv", help="The format of the results.")
    parser.add_argument("--with-headers", action="store_true", help="Output the result with headers.")
    parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")


def as_view(fields: list[str], series: Series) -> dict[str, Any]:
    series = dataclasses.asdict(series)
    return {field: series[field] for field in fields}


def output_as_csv(fields: list[str], all_series: list[Series], delimeter=",", with_headers=False) -> None:
    import csv, sys
    writer = csv.DictWriter(sys.stdout, fields, delimiter=delimeter)
    if with_headers:
        writer.writeheader()

    for series in all_series:
        writer.writerow(as_view(fields, series))


def output_as_toml(fields: list[str], all_series: list[Series]) -> None:
    from datetime import date

    for series in all_series:
        print(f"['{series.stub_info()}']")
        series = as_view(fields, series)
        for field in fields:
            value = series[field]
            if isinstance(value, date):
                formatted = f'"{value}"'
            elif isinstance(value, bool):
                formatted = f'{str(value).lower()}'
            else:
                formatted = repr(value)
            print(f"{field} = {formatted}")
        print()


def info(args: ap.Namespace) -> None:
    cache.load()
    tracked = list(cache.find(args.title, strict=args.strict))

    fields = args.fields if args.fields is not None else SERIES_FIELDS
    output_csvlike = lambda delimeter: output_as_csv(fields, tracked, with_headers=args.with_headers, delimeter=delimeter)
    if args.format == "csv":
        output_csvlike(delimeter=",")
    elif args.format == "tsv":
        output_csvlike(delimeter="\t")
    elif args.format == "toml":
        output_as_toml(fields, tracked)