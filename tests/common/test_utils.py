from dataclasses import dataclass
from unittest import mock
import builtins
import pytest
from common import utils
from typing import Iterable

@pytest.mark.parametrize("user_input, expected", [
    ("y", True),
    ("Y", True),
    ("n", False),
    ("N", False),
])
def test_confirm_responses(user_input, expected):
    with mock.patch.object(builtins, "input", return_value=user_input):
        assert utils.confirm("Proceed?") == expected

def test_confirm_default_on_empty_input():
    with mock.patch.object(builtins, "input", return_value=""):
        assert utils.confirm("Proceed?", default="y") == True
        assert utils.confirm("Proceed?", default="n") == False

@pytest.mark.parametrize("user_inputs, expected", [
    (('ahbsdkhjgq', 'no', 'Nein', 'y'), True),
    (('Yes', 'n'), False),
])
def test_confirm_retries_on_bad_entry(monkeypatch, user_inputs: Iterable[str], expected: bool):
    call_count = 0
    def input_mock(*args, **kwargs):
        nonlocal call_count
        rv = user_inputs[call_count]
        call_count += 1
        return rv

    monkeypatch.setattr(builtins, 'input', input_mock)
    assert utils.confirm("Proceed?") == expected

@dataclass
class MockOption:
    name: str
    def stub_info(self) -> str:
        return f"Stub: {self.name}"
    def full_info(self) -> str:
        return f"Full: {self.name}"

def test_select_valid_option():
    options = [MockOption("Option A"), MockOption("Option B")]

    with mock.patch.object(builtins, "input", return_value='1'):
        selected = utils.select("Choose an option:", options)
        assert selected == options[1]

def test_select_out_of_range_option(monkeypatch, capsys):
    options = [MockOption("Option A"), MockOption("Option B")]
    user_inputs = ["2", "3", "1"]

    call_count = 0
    def input_mock(*args, **kwargs):
        nonlocal call_count
        assert call_count < len(user_inputs), "Called input more than expected"
        rv = user_inputs[call_count]
        call_count += 1
        return rv

    monkeypatch.setattr(builtins, "input", input_mock)
    selected = utils.select("Choose an option:", options)
    assert selected == options[1]

    captured = capsys.readouterr()
    assert "Invalid selection" in captured.out