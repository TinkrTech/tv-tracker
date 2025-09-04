from functools import reduce, wraps
from typing import Protocol, Iterable, Callable
USE_ANIMATIONS = True

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


def with_spinner[T](func: Callable[..., T], message: str = "") -> Callable[..., T]:
    """
    Add an animated spinner to any function. Prints message and updates the end of the line in stdout until the function completes.
    On success                        - Replace spinner with the PASS character
    On Exception or KeyboardInterrupt - Replace spinner with the FAIL character
    """
    import sys
    import threading
    import time

    PASS = "🟢" # "✅"
    FAIL = "🔴" # "❌"

    def spin(is_done: Callable[..., bool]) -> None:
        spinner = ['/','-','\\','|']
        i = 0
        print(message, end="  ")
        while not is_done():
            print(f"\b{spinner[i]}", end="", file=sys.stdout, flush=True)
            i = (i + 1) % len(spinner)
            time.sleep(0.15)

    @wraps(func)
    def with_spinner(*args, **kwargs) -> T:
        done = False
        spin_thread = threading.Thread(target=lambda: spin(lambda: done))
        try:
            spin_thread.start()
            result = func(*args, **kwargs)
            print(f"\b{PASS}")
        except Exception as e:
            print(f"\b{FAIL}")
            raise e
        except KeyboardInterrupt as e:
            print(f"\b\b\b{FAIL} ^C")
            raise e
        finally:
            done = True
            spin_thread.join()
        return result

    @wraps(func)
    def without_spinner(*args, **kwargs) -> T:
        print(message)
        return func(*args, **kwargs)

    if USE_ANIMATIONS:
        return with_spinner
    else:
        return without_spinner
