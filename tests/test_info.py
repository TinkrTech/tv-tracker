# Copyright (C) 2026 Jade T
# SPDX-License-Identifier: GPL-3.0+
# Author: Jade T <jade@tinkrtech.net>
import pytest
import argparse as ap

import info

def mock_args(title, **kwargs) -> ap.Namespace:
    parser = ap.ArgumentParser()
    info.add_args(parser)

    args = [title]
    for key, value in kwargs.items():
        args.extend([f"--{key}", value])

    return parser.parse_args(args)


def test_invalid_field_name_is_rejected():
    ...

def test_valid_toml():
    ...

def test_toml_with_headers():
    ...

def test_toml_fields_are_respected():
    ...

def test_valid_csv():
    ...

def test_valid_tsv():
    ...

def test_csv_with_headers():
    ...

def test_csv_fields_are_respected():
    ...
