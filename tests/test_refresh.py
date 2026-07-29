# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
import argparse as ap

import refresh

def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    refresh.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)

def test_only_keep_updated_series_are_updated():
    ...

def test_force_refreshes_everything():
    ...
