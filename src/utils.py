from functools import reduce

def compose(*funcs):
    def _compose(f, g):
        return lambda *a, **k: f(g(*a, **k))
    return reduce(_compose, funcs)

def intersect(*funcs):
    def _intersect(f, g):
        return lambda *a, **k: f(*a, **k) and g(*a, **k)
    return reduce(_intersect, funcs)

def confirm(prompt: str) -> bool:
    while opt := input(prompt).strip().lower() not in ['','y', 'n']:
        print(f"Invalid selection '{opt}'")
    return opt != 'n'

def select[T](prompt: str, options: list[T]) -> T:
    ...