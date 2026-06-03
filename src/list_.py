# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import argparse as ap

from common import cache


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", nargs="*", help="Only list the info for series containing this title.")
    parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")


def list_(args: ap.Namespace) -> None:
    if len(args.title) > 0:
        tracked = cache.find(args.title, strict=args.strict)
    else:
        tracked = cache.result_of(cache.select_series())

    for i, series in enumerate(tracked, 1):
        print(f"{i} - {series.stub_info()}")