# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>

import argparse as ap
import logging as log

from common import cache
from common.model import Series


def add_args(parser: ap.ArgumentParser) -> None:
    parser.add_argument("title", help="The series to update.")
    parser.add_argument("-o", "--order", help="Change which season order should be used when fetching updates.")
    parser.add_argument("-l", "--language", help="Set which translation to use")
    parser.add_argument("-s", "--strict", default=False, action="store_true", help="Only match titles which exactly match.")


def _modify(series: Series, args: ap.Namespace):
    updated = series.model_copy()
    if args.language:
        updated.config.language = args.language

    if args.order:
        if cache.is_valid_order(series, args.order):
            updated.config.order = args.order
        else:
            log.warning("Not using invalid order...")
    return updated


def modify(args: ap.Namespace):
    all_series = cache.find(args.title, strict=args.strict)
    updated_series = [_modify(series, args) for series in all_series]
    cache.update(updated_series)