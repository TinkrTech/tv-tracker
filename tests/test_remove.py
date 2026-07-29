# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
import argparse as ap


import remove


def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    remove.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)


def test_remove_untracked_skips():
    ...

def test_remove_mixed_skips_non_matches():
    ...

def test_remove_ambiguous_warns_and_skips():
    ...

def test_remove_ambiguous_title_with_year_disambiguates():
    ...

def test_remove_strict_has_no_ambiguity():
    ...
