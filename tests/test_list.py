# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
import argparse as ap

import list_

def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    list_.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)

def test_list_defaults_to_showing_all_stubs():
    ...

def test_list_one_title_shows_at_least_one_match():
    ...

def test_list_one_title_strict_shows_at_most_one_match():
    ...