from functools import reduce
from typing import Protocol, Iterable

class Stubbable(Protocol):
    def stub_info(self) -> str:
        """Return a single-line string that uniquely categorizes the object"""

    def full_info(self) -> str:
        """Return a single-line string that uniquely categorizes the object"""


def compose(*funcs):
    def _compose(f, g):
        return lambda *a, **k: f(g(*a, **k))
    return reduce(_compose, funcs)

def intersect(*funcs):
    def _intersect(f, g):
        return lambda *a, **k: f(*a, **k) and g(*a, **k)
    return reduce(_intersect, funcs)

def confirm(prompt: str, default='y') -> bool:
    options = ('y', 'n')
    default = default.lower()
    assert default in options, "Default was not included in the valid options. Typo?"

    def capitalize_default_option():
        result = []
        for option in options:
            if option == default:
                result.append(option.upper())
            else:
                result.append(option)
        return result

    fmt_options = '/'.join(capitalize_default_option())

    prompt += f" [{fmt_options}]>"

    while opt := input(prompt).strip().lower():
        if opt == '':
            opt = default
        elif opt in options:
            break
        else:
            print(f"Invalid selection '{opt}'")

    return opt == 'y'


def select(prompt: str, options: Iterable[Stubbable]) -> Stubbable:
    prompt += "\n" + "\n".join([f"{i}: {option.stub_info()}" for i, option in enumerate(options)])
    prompt += "\nor 'info <selection>' for more details\n>"
    while opt := input(prompt).strip().lower():
        if opt.isdigit():
            break

        if (not opt.startswith("info")):
            print(f"Invalid selection '{opt}")
            continue

        opt = opt.removeprefix("info ")
        if not opt.isdigit():
            print(f"Invalid selection 'info {opt}'")
            continue

        print(options[int(opt)].full_info())
        if confirm("Select this? ", default='n'):
            break
    return options[int(opt)]
