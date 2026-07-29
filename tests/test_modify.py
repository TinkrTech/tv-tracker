# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
import argparse as ap

import modify


def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    modify.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)

def test_invalid_order_is_not_used():
    ...

def test_valid_order_is_used():
    ...

def test_only_three_letter_code_is_accepted_for_language():
    ...

def test_language_is_used():
    ...
