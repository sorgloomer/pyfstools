from collections import namedtuple

from fs import open_fs

Iteration = namedtuple("Iteration", ["first", "last", "value"])


def mark_iterable_ends(iterable):
    iterator = iter(iterable)
    try:
        value = next(iterator)
    except StopIteration:
        return
    first = True
    for item in iterator:
        yield Iteration(first, False, value)
        first = False
        value = item
    yield Iteration(first, True, value)


def param_open_fs(fs):
    if isinstance(fs, str):
        return open_fs(fs)
    return fs


UNITS = [
    (1024 ** 0, 'b'),
    (1024 ** 1, 'K'),
    (1024 ** 2, 'M'),
    (1024 ** 3, 'G'),
    (1024 ** 4, 'T'),
    (1024 ** 5, 'P'),
    (1024 ** 6, 'E'),
    (1024 ** 7, 'Z'),
    (1024 ** 8, 'Y'),
]


def find_range(size):
    if size is None:
        return None
    for u in UNITS:
        if size < 7000 * u[0]:
            return u


def format_size_tuple(size):
    if size is None:
        return None
    u = find_range(size)
    return size / u[0], u[1]


def format_size(size):
    if size is None:
        return '-'
    n, u = format_size_tuple(size)
    return f"{n:4.4f}{u}"


def none_to_empty(x):
    return () if x is None else x


def compose_decorators(*fns):
    def _composed(x):
        for fn in fns[::-1]:
            x = fn(x)
        return x
    return _composed
