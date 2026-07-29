# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
import argparse as ap

import fetch_episodes


def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    fetch_episodes.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)


def test_unmatched_gives_warning_and_exits():
    ...

def test_ambiguous_title_asks_for_selection():
    ...

def test_invalid_order_uses_default_order_instead():
    ...

def test_valid_order_uses_expected_order():
    ...

def test_all_seasons_returned_when_no_season_is_selected():
    ...

def test_only_selected_season_is_returned():
    ...

def test_non_existant_season_gives_warning():
    ...

def test_only_name_is_returned_when_flagged():
    ...

def test_formatting():
    ...
